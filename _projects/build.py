#!/usr/bin/env python3
"""Build the project pages on willtoforge.com from each project's public repo.

Each project in projects.json has a public showcase repo (for example
DougieWilDaBeast/skill-engine-public) holding README.md and images/. This script
turns that README into /<slug>/index.html in the site's own look, copies the
pictures to /<slug>/img/, makes the card picture, and rewrites the Projects
cards on the home page and the sitemap.

    pip install markdown pillow
    python3 _projects/build.py               # clones each public repo
    python3 _projects/build.py --src DIR     # uses existing clones in DIR/<repo>

The showcase repos are written by a publish step from the private repos, so the
words are changed there, not here. Run this again after a showcase changes.
"""
import argparse
import datetime
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from PIL import Image

OWNER = "DougieWilDaBeast"
SITE = "https://willtoforge.com"
ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent

# Sections of a showcase README that are about the repo, not the project.
DROP_SECTIONS = {"what is in this repository"}


def load_readme(repo_dir: Path) -> tuple[str, str]:
    text = (repo_dir / "README.md").read_text(encoding="utf-8")
    m = re.match(r"\s*# (.+)\n", text)
    if not m:
        sys.exit(f"{repo_dir.name}: README has no '# Title' first line")
    title, body = m.group(1).strip(), text[m.end():]
    # Drop mermaid diagrams: GitHub draws them, a plain page can't.
    body = re.sub(r"```mermaid\n.*?```\n?", "", body, flags=re.S)
    # Drop repo-only sections, from their heading to the next ## heading.
    out, skip = [], False
    for line in body.splitlines(keepends=True):
        h = re.match(r"## (.+)", line)
        if h:
            skip = h.group(1).strip().lower() in DROP_SECTIONS
        if not skip:
            out.append(line)
    body = "".join(out)
    body = body.replace('src="images/', 'src="img/').replace("](images/", "](img/")
    return title, body


def render(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "md_in_html"],
        extension_configs={"toc": {"permalink": False}},
        output_format="html",
    )


def page(p: dict, body_html: str) -> str:
    t, tag = html.escape(p["title"]), html.escape(p["tagline"])
    url = f"{SITE}/{p['slug']}/"
    repo = f"https://github.com/{OWNER}/{p['repo']}"
    short = re.split(r"[:.,]", p["tagline"])[0]
    return TEMPLATE.format(
        title=t, tagline=tag, tagline_short=html.escape(short), url=url, repo=repo,
        repo_short=f"{OWNER}/{p['repo']}", status=html.escape(p["status"]), body=body_html,
    )


def card_html(p: dict) -> str:
    return (
        f'<a class="app" href="/{p["slug"]}/">\n'
        f'<img src="/{p["slug"]}/img/card.png" alt="" width="72" height="72">\n'
        f'<div><b>{html.escape(p["title"])}</b><span>{html.escape(p["tagline"])}</span>'
        f'<em>{html.escape(p["status"])} · see how it works</em></div>\n</a>'
    )


def make_card(src: Path, box: list, dest: Path) -> None:
    im = Image.open(src).convert("RGB").crop(tuple(box)).resize((144, 144), Image.LANCZOS)
    im.save(dest, optimize=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, help="folder holding clones of the public repos")
    args = ap.parse_args()
    cfg = json.loads((HERE / "projects.json").read_text(encoding="utf-8"))
    tmp = None
    src = args.src
    if src is None:
        tmp = tempfile.TemporaryDirectory()
        src = Path(tmp.name)
        for p in cfg["projects"]:
            subprocess.run(["git", "clone", "-q", "--depth", "1",
                            f"https://github.com/{OWNER}/{p['repo']}.git", str(src / p["repo"])],
                           check=True)
    today = datetime.date.today().isoformat()
    for p in cfg["projects"]:
        repo_dir = src / p["repo"]
        _, body = load_readme(repo_dir)
        out = ROOT / p["slug"]
        if out.exists():
            shutil.rmtree(out)
        (out / "img").mkdir(parents=True)
        for f in sorted((repo_dir / "images").iterdir()):
            if f.name in body:  # copy only the pictures the page uses
                shutil.copy2(f, out / "img" / f.name)
        make_card(repo_dir / "images" / p["card"]["image"], p["card"]["box"], out / "img" / "card.png")
        (out / "index.html").write_text(page(p, render(body)), encoding="utf-8")
        print(f"built /{p['slug']}/")

    # Home page cards, between the markers.
    index = ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    cards = "\n".join(card_html(p) for p in cfg["projects"])
    new, n = re.subn(r"<!-- projects:start -->.*?<!-- projects:end -->",
                     lambda m: f"<!-- projects:start -->\n{cards}\n<!-- projects:end -->",
                     text, flags=re.S)
    if n != 1:
        sys.exit("index.html: projects markers not found")
    index.write_text(new, encoding="utf-8")

    # Sitemap: the home page plus each project page.
    urls = [f"{SITE}/"] + [f"{SITE}/{p['slug']}/" for p in cfg["projects"]]
    rows = "\n".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{rows}\n</urlset>\n", encoding="utf-8")
    if tmp:
        tmp.cleanup()


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}: {tagline_short} · WillToForge</title>
<meta name="description" content="{tagline}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/img/icon-32.png" sizes="32x32">
<link rel="icon" href="/img/icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="/img/icon-180.png">
<meta name="theme-color" content="#1b1e20">
<meta property="og:title" content="{title} · WillToForge">
<meta property="og:description" content="{tagline}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}img/card.png">
<link rel="preload" href="/fonts/instrument-serif-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/_projects/project.css">
</head>
<body>
<div class="wrap">
<nav><a href="/" class="home"><span class="ogham" aria-hidden="true">᚛ᚃᚑᚏᚌᚓ᚜</span>WillToForge</a><span class="crumb">Projects</span></nav>
<header>
<h1>{title}</h1>
<p class="status">{status}</p>
</header>
<article>
{body}
</article>
<aside class="repo">
<p>The code is kept private. This page is also on GitHub at <a href="{repo}">{repo_short}</a>. All rights reserved.</p>
</aside>
<footer><span class="ogham" aria-hidden="true">᚛ᚃᚑᚏᚌᚓ᚜</span><a href="/">WillToForge</a> · <a href="mailto:hello@willtoforge.com">hello@willtoforge.com</a></footer>
</div>
</body>
</html>
"""


if __name__ == "__main__":
    main()
