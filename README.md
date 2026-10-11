# Spidlen Games website

The static website at https://spidlengames.github.io, served by GitHub Pages straight from this
repository (no build step).

- `/`: Spidlen Games
- `/cannonball-captains/`: Cannonball Captains, with the download button
- `/cannonball-captains/privacy/`: Cannonball Captains privacy policy (linked from Google Play)
- `/cannonball-captains/play/`: the browser version (`?lang=cs` etc. picks its first language)
- `/cs/`, `/de/`, `/es/`, `/fr/`, `/it/`: the same pages in Czech, German, Spanish, French and Italian

**Languages:** the English pages are the originals. The translated copies are made by
`python3 tools/languages.py` from the table of texts in that script, which also adds the
language picker (top right). After changing an English page, update the table and rerun it;
it lists any texts it can no longer find. Screenshots per language: `assets/img/screens/<code>/`.

Game downloads are attached to this repository's
[Releases](https://github.com/spidlengames/spidlengames.github.io/releases) (public edition only).
The game's source code lives in a separate private repository; its `tools/dev.sh publish` builds
a release, uploads it here and updates the download button.

Fonts: Cannonball Heading (Lilita One with Czech letters added, made by the game repo's
`tools/make_font.py`) and Nunito, SIL Open Font License (see `assets/fonts`).
