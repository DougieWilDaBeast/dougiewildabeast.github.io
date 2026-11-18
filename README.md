# willtoforge.com

Home page for WillToForge, served by GitHub Pages from `main` at https://willtoforge.com/

- `index.html`: the home page, with one card per app
- `CNAME`: sets the custom domain. Because this is the account's user site, every other Pages site on the account is served under the same domain, for example `eisenhower-matrix` at https://willtoforge.com/eisenhower-matrix/
- `robots.txt`, `sitemap.xml`: for search engines (`sitemap.xml` is written by `_projects/build.py`)

To add an app: copy the `.app` card in `index.html` and add the app's sitemap to `robots.txt`.

## Projects

The Projects section lists bigger experiments that aren't apps to download. Each has a page at `/<slug>/` (for example https://willtoforge.com/skill-engine/) built from its public showcase repo (`DougieWilDaBeast/<name>-public`, whose README is written by a publish step from the private repo).

- `_projects/projects.json`: the list: slug, showcase repo, title, one-line tagline, status, and which picture and crop make the card
- `_projects/build.py`: turns each showcase README into `/<slug>/index.html`, copies its pictures to `/<slug>/img/`, makes `card.png`, and rewrites the cards between the `projects:start` and `projects:end` markers in `index.html` and the whole `sitemap.xml`
- `_projects/project.css`: the project pages' styles

To add or refresh one: change `projects.json` if needed, then

```
pip install markdown pillow
python3 _projects/build.py
```

The words come from the showcase repos, so change them there and rebuild. The project pages never link to private sites.

Contact: hello@willtoforge.com

## Look

Stone and sandstone, with the mark written in Ogham: `᚛ᚃᚑᚏᚌᚓ᚜` (FORGE, upright, read bottom to top) and `᚛ᚃᚔᚂᚂᚈᚑᚃᚑᚏᚌᚓ᚜` (WILLTOFORGE). Fonts are self-hosted in `fonts/` (Instrument Serif, Sora, Noto Sans Ogham; SIL Open Font License), so the page makes no requests to other sites. Icons and the share image are in `img/`.
