# Writing for Cypher Rants

How a post gets made, from idea to published page. `DESIGN.md` is the visual spec; this file is the author's manual. Live site: https://appcypher.dev · repo root is a Jekyll site built by GitHub Pages from `main`.

## The shape of a post

One Markdown file: `_posts/YYYY-MM-DD-slug.md`. Front matter:

```yaml
---
title: Sandboxes are not containers          # sentence case, no period
description: One line under the title and on the card.   # 90–140 chars, a real sentence
cover: bob            # who sits on the card and above the article; any name in _data/cast.json; default stephen
rant: true            # optional: RANT stamp on the cover, "rant" chip on the card
mood: rant            # optional: use the cover character's furious variant
tags: [sandboxing, kvm]   # optional, lowercase
---
```

Draft in `_drafts/` (rendered only with `--drafts`, never on the live site, but visible in the public repo). Publish by moving the file to `_posts/` with the date in the name and pushing `main`; GitHub builds it in about a minute.

`_drafts/first-rant.md` is a working cheat sheet that uses every convention below — copy it.

## Conventions the layout understands

Plain Markdown is enough. These extras exist; use them when they carry meaning, not for decoration.

| you write | you get |
|---|---|
| `## heading` | an inverted "mark" heading. Keep h2s short (1–3 words), lowercase reads best |
| a paragraph, then a line `{:.aside}` | that paragraph becomes a handwritten sidenote in the 240px margin. ≤ 2 sentences |
| `{% include react.html who="bob" say="three? that's it?" %}` | bob's face in the margin with a small speech bubble. One per screen, never two in a row |
| `{% capture d %}`<br>`alice: what goes in _drafts/?`<br>`bob: anything you're not ready to publish.`<br>`{% endcapture %}{% include dialogue.html text=d %}` | a conversation: faces and bubbles alternating sides. First speaker sits left. Lines can contain inline Markdown |
| `> note: the cover key picks the doodle.` | a sticky note (ochre). Ordinary `>` quotes keep the pen rule |
| `{% include figure.html scene="key-exchange" caption="fig. 1 — alice sends bob a key" %}` | a full-width figure (924px, breaks out of the text column) from `_includes/doodles/scenes/key-exchange.svg` |
| `{% include figure.html src="/assets/posts/slug/thing.png" caption="…" %}` | same, for a scanned or hand-drawn image |
| `:key:` `:envelope:` `:eve:` inline | tiny line glyphs in the sentence. Any of the 66 things or any cast name; the sprite is fetched only on pages that use one |
| `` `code` `` and fenced blocks | monospace on the code wash; language hints work (`rust`, `bash`, `python`) |

Rules of thumb: a figure replaces a paragraph, so its caption must be a real sentence that could stand in for the drawing. Dialogue is for explaining a protocol or an argument, two to five turns, never small talk. Sidenotes are asides, not footnotes with citations. Highlight nothing; the layout has no bold that reads well in Patrick Hand, so emphasis comes from structure and short sentences.

## The cast

`_data/cast.json` — the author (`stephen`) plus 24 recurring characters, the classic crypto placeholders drawn as people: alice sends, bob receives, carol and dave are the third and fourth party, eve listens in, mallory attacks, trent is the trusted third party, peggy proves and victor verifies, walter is the warden, oscar the opponent, sybil is many, grace the government, heidi mischief, ivan issues, judy judges, frank and erin are generic, chuck makes trouble, craig cracks passwords, faythe advises, olivia is the oracle, wendy blows the whistle, pat wears the helmet.

Use them by their conventional role: if a post is about an eavesdropper it is eve, if it is about an active attacker it is mallory. Do not invent new people for one post. To add a character, add an entry to `cast.json` (copy a neighbour, change one distinctive thing) and run `python3 tools/gen_doodles.py`; commit the regenerated SVGs.

## Drawing a figure

Figures are SVGs in `_includes/doodles/scenes/`, generated with the pen engine so they match the rest of the site in both themes. A scene is a few lines of Python:

```python
import json, sys; sys.path.insert(0, "tools")
import doodle as D
from doodle import Pen
cast = {c["name"]: c for c in json.load(open("_data/cast.json"))["cast"]}
def recipe(c): return dict(head=c["head"], skin=c["skin"], hair_=c["hair"], hair_color=c.get("hair_color", "ink"), eye=c["eye"], brow=c.get("brow", "flat"), mouth_=c["mouth"], fh=c.get("fh"), extra=tuple(c.get("extra", [])), wash=c["wash"], back=c["back"])

p = Pen(seed=7, style=3, rough=1.0)          # style 3 = wash, the site default; rough 0 for diagrams, 2+ for panic
W, H = 960, 300
# faces and objects "boil" (three inkings cycled by CSS) — wrap only those in D.boil; arrows, words, bubbles and stamps stay still
s  = D.place(D.boil(lambda pen: D.face(pen, **recipe(cast["alice"]), look=(1.5, 0)), 101), 40, 40, 1.5)   # scale 1.5 → chin at about (x+90, y+188)
s += D.place(D.boil(lambda pen: D.face(pen, **recipe(cast["bob"]), look=(-1.5, 0)), 202), 740, 40, 1.5)
s += D.arrow(p, (250, 140), (730, 140), w=2.2) + D.place(D.boil(lambda pen: D.obj(pen, "key", "ochre"), 303), 460, 82, 0.9)
s += D.text(490, 118, "here's the key", 24, "hand", D.PENC, "middle")            # "hand" = Caveat, "mono" = Plex Mono
s += D.bubble(p, 60, 232, 210, 50, to=(132, 192)) + D.text(165, 264, "don't lose it.", 19, "hand", "currentColor", "middle")
s += D.stamp(p, 420, 200, "ok", D.GREEN, rot=-6, size=13)
open("_includes/doodles/scenes/key-exchange.svg", "w").write(f'<svg viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">{s}</svg>\n')
```

Pieces available: `boil` (three inkings of a face or object that differ by a third of the wobble, cycled at ~2 fps; never for arrows, text or bubbles), `face`, `obj` (66 things: envelope, key, lock, server, cloud, database, sandbox, cube, vm, process, bug, shield, fire, …), `arrow` (`curve=`, `dashed=`, `both=`), `lightning` for "blocked", `bubble` (`to=(x, y)` = the speaker's chin — the tail always points at who is talking), `text`, `stamp`, `pin_num`, `tape`, `circle_emph`, `crossout`, `underline_scribble`, `bracket`, `sparkles`. Colours: `D.PENC` (pen blue, for the one thing the paragraph is about), `D.RED` (only for "no"), `D.GREEN` (only for "yes"), `"currentColor"` for everything else. Never put a face on an object. Run `python3 tools/test_doodle.py` after touching the engine.

## Voice

The site is called Cypher Rants; the author is Stephen Akinyemi (appcypher), who builds microsandbox and writes about building things, lessons learned, and the occasional rant. Everything on the page is lowercase and handwritten, so the prose should read like a person talking: short paragraphs, concrete examples, first person, opinions stated as opinions. A rant is allowed to be annoyed; it is not allowed to be vague about what it is annoyed at.

Do not invent facts, biography, quotes, benchmarks or events. If a post needs a number, the author supplies it or the post says it doesn't have one. If a post is about a system, link the code.

## Publishing checklist

1. Build with drafts and look at it: `GEM_HOME="$PWD/vendor/gems" GEM_PATH="$PWD/vendor/gems" JEKYLL_NO_BUNDLER_REQUIRE=true /opt/homebrew/opt/ruby/bin/ruby vendor/gems/bin/jekyll build --destination preview --strict_front_matter --drafts` then serve `preview/` (e.g. `python3 -m http.server -d preview 4000`). `bundle exec jekyll serve --drafts` works if Bundler is set up.
2. Check both themes (the toggle in the rail), desktop and 390px, and that every figure caption reads as a sentence.
3. Move the draft to `_posts/YYYY-MM-DD-slug.md`. Commit with a signed commit (`git commit -S`), conventional-commit style (`post: sandboxes are not containers`). Push `main`.
4. The live page is `https://appcypher.dev/posts/<slug>/`; the feed at `/feed.xml` updates with it.

Keep `preview/`, `vendor/`, `.bundle/` out of Git (already ignored). Never add an email address or a contact form. Do not add JavaScript, fonts or dependencies for a post; if a post needs something the layout cannot do, say so and stop.
