# Cypher Rants

Personal Jekyll blog for https://appcypher.github.io — a notebook with a fixed left rail, monospaced type, paper grain, and hand-drawn doodles generated from a small pen engine. Light by default, with a dark theme. The design is documented in `DESIGN.md`.

## Publish on GitHub Pages

Push to `main`. GitHub builds Jekyll from the repository root; nothing else is required.

## Write a post

Copy `_drafts/first-rant.md` to `_posts/YYYY-MM-DD-your-post-title.md`, set the title and description, replace the body, commit and push. The draft is also a cheat sheet for the extra conventions:

- `cover: bob` in front matter picks the doodle on the post card and article header (any name in `_data/cast.json`, default the author). `rant: true` adds the RANT stamp and chip; `mood: rant` uses the furious portrait.
- A paragraph ending in `{:.aside}` becomes a handwritten sidenote in the margin.
- `{% include react.html who="bob" say="…" %}` puts a character with a speech bubble in the margin.
- `{% capture d %}alice: … / bob: …{% endcapture %}{% include dialogue.html text=d %}` renders a conversation.
- `{% include figure.html src="/assets/….png" caption="fig. 1 — …" %}` (or `scene="name"`) is a full-width figure.
- A blockquote starting with `note:` is a sticky note. `:key:`, `:envelope:`, `:alice:` … become inline glyphs.
- `## headings` render as inverted marks; the Markdown stays plain.

Files under `_drafts` are not rendered but are visible in the public repository; keep private drafts elsewhere.

## Doodles

`_data/cast.json` describes the author and the recurring characters as recipes (head, skin, hair, eyes, mouth, wash, …). `tools/gen_doodles.py` draws them with `tools/doodle.py` into `_includes/doodles/` (people, 66 things, an inline-glyph sprite, the empty-state scene) and writes the favicon. Edit the JSON, run `python3 tools/gen_doodles.py`, commit the SVGs. Every colour in a doodle is a CSS token, so the same SVG is correct in both themes.

## Preview locally

```sh
bundle install
bundle exec jekyll serve --drafts
```

Open http://localhost:4000. `/components/` shows every component on one page.
