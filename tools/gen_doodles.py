#!/usr/bin/env python3
"""Generate the site's doodle SVGs from _data/cast.json with tools/doodle.py.

Writes inline-able SVG into _includes/doodles/ (people, things, the empty-state scene),
the glyph sprite into assets/doodles/glyphs.svg (fetched on demand), and the favicon. Run from the repo root: python3 tools/gen_doodles.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import doodle as D

class Pen(D.Pen):
    """site pen: slightly coarser stroke sampling than the design sheets, to keep inlined SVG small"""
    def _step(self, step):
        return super()._step(step) * 1.5

OUT = os.path.join(ROOT, "_includes", "doodles")
THINGS = ["envelope", "sealed", "mail-open", "key", "lock", "unlock", "shield", "fingerprint", "hash", "laptop", "keyboard", "terminal", "phone", "server", "rack", "cpu", "router", "wifi", "dish", "cloud", "database", "doc", "folder", "clipboard", "box", "sandbox", "cube", "vm", "process", "git", "bug", "gear", "magnifier", "clock", "hourglass", "calendar", "bulb", "coin", "coffee", "globe", "signpost", "plant", "flag", "chain", "fire", "trash", "dice", "book", "pencil", "stamp", "bell", "battery", "hammer", "wrench", "pin", "chart", "tag", "rocket", "heart", "star", "eye", "ear", "handwave", "check", "cross", "question"]
WASHES = ["blue", "ochre", "sage", "mauve", "clay", "gray"]

def wrap(inner, vb="0 0 120 120"):
    return f'<svg viewBox="{vb}" aria-hidden="true" focusable="false">{inner}</svg>\n'

def recipe(c):
    kw = dict(head=c.get("head", "round"), skin=c.get("skin", "s4"), hair_=c.get("hair", "short"), hair_color=c.get("hair_color", "ink"),
              eye=c.get("eye", "oval"), brow=c.get("brow", "flat"), nose_=c.get("nose", "l"), mouth_=c.get("mouth", "smile"),
              fh=c.get("fh"), fh_color=c.get("fh_color"), extra=tuple(c.get("extra", [])), wash=c.get("wash", "sage"), back=c.get("back", "blob"))
    return kw

def seed_of(name):
    return sum(ord(ch) * (i + 1) for i, ch in enumerate(name)) % 9973

def main():
    data = json.load(open(os.path.join(ROOT, "_data", "cast.json")))
    people = [data["author"]] + data["cast"]
    for d in ("people", "things", "scenes"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    # people: wash style, default hand
    for c in people:
        kw = recipe(c)
        rough = float(c.get("rough", 1))
        inner = D.face(Pen(seed_of(c["name"]), 3, rough=rough), **kw)
        open(os.path.join(OUT, "people", f'{c["name"]}.svg'), "w").write(wrap(inner))
        # a furious variant for the rant marker
        kw2 = dict(kw); kw2.update(eye="oval", brow="angry", mouth_="shout", extra=tuple(kw["extra"]) + ("cloud", "bangs", "steam"))
        open(os.path.join(OUT, "people", f'{c["name"]}-rant.svg'), "w").write(wrap(D.face(Pen(seed_of(c["name"]) + 1, 3, rough=2.2), **kw2)))

    # things
    for i, k in enumerate(THINGS):
        inner = D.obj(Pen(seed_of(k), 3), k, WASHES[i % len(WASHES)])
        open(os.path.join(OUT, "things", f"{k}.svg"), "w").write(wrap(inner))

    # glyph sprite: style 1, no wash, for inline :name: tokens
    syms = []
    for k in THINGS:
        syms.append(f'<symbol id="g-{k}" viewBox="0 0 120 120">{D.obj(Pen(seed_of(k), 1, rough=0), k, "")}</symbol>')
    for c in people:
        kw = recipe(c); kw.update(back="none", skin=None)
        syms.append(f'<symbol id="g-{c["name"]}" viewBox="0 0 120 120">{D.face(Pen(seed_of(c["name"]), 1, rough=0), **kw)}</symbol>')
    os.makedirs(os.path.join(ROOT, "assets", "doodles"), exist_ok=True)
    open(os.path.join(ROOT, "assets", "doodles", "glyphs.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' + "".join(syms) + "</svg>\n")

    # empty-state scene: alice asks, bob answers
    p = Pen(77, 3); W, H = 960, 300
    a = recipe(data["cast"][0]); b = recipe(data["cast"][1])
    s = D.place(D.face(p, look=(1.5, 0), **a), 40, 40, 1.5)
    s += D.place(D.face(p, look=(-1.5, 0), **b), 740, 40, 1.5)
    s += D.arrow(p, (250, 140), (730, 140), w=2.2) + D.text(490, 118, "any update?", 24, "hand", D.PENC, "middle")
    s += D.bubble(p, 30, 236, 200, 46, "tl", "round") + D.text(130, 265, "is the first rant out yet?", 12, "mono", "currentColor", "middle")
    s += D.bubble(p, 700, 236, 230, 46, "tl", "round") + D.text(815, 265, "still brewing. come back soon.", 12, "mono", "currentColor", "middle")
    s += D.stamp(p, 420, 200, "0 posts", "currentColor", rot=-6, size=13)
    open(os.path.join(OUT, "scenes", "empty-state.svg"), "w").write(wrap(s, f"0 0 {W} {H}"))

    # favicon: khaki tile, ink "cr." tilted
    fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="13" fill="#d2c79d"/>'
           '<text x="32" y="43" text-anchor="middle" font-family="IBM Plex Mono, Menlo, ui-monospace, monospace" font-weight="700" font-size="33" letter-spacing="-2" fill="#171612" transform="rotate(-6 32 32)">cr.</text></svg>\n')
    open(os.path.join(ROOT, "assets", "favicon.svg"), "w").write(fav)
    print(f"people {len(people)}×2, things {len(THINGS)}, sprite {len(syms)} symbols, scene, favicon")

if __name__ == "__main__":
    main()
