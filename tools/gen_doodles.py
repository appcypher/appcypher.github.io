#!/usr/bin/env python3
"""Generate the site's doodle SVGs from _data/cast.json with tools/doodle.py.

Writes inline-able SVG into _includes/doodles/ (people, things, the empty-state scene),
the glyph sprite into assets/doodles/glyphs.svg (fetched on demand), and the favicon SVG
(rasterise it to assets/favicon.png and apple-touch-icon.png with: qlmanage -t -s 64 -o . assets/favicon.svg). Run from the repo root: python3 tools/gen_doodles.py
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
    for d in ("people", "things", "scenes", "marks"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    # people: wash style, default hand
    FRAMES = 3  # line boil: the same drawing inked three times, cycled by CSS (.f0 .f1 .f2)
    boilers = {data["author"]["name"]}
    for c in people:
        kw = recipe(c)
        rough = float(c.get("rough", 1))
        n = FRAMES if c["name"] in boilers else 1
        open(os.path.join(OUT, "people", f'{c["name"]}.svg'), "w").write(wrap(D.boil_face(seed_of(c["name"]), n, rough=rough, **kw)))
        # a furious variant for the rant marker
        kw2 = dict(kw); kw2.update(eye="oval", brow="angry", mouth_="shout", extra=tuple(kw["extra"]) + ("cloud", "bangs", "steam"))
        open(os.path.join(OUT, "people", f'{c["name"]}-rant.svg'), "w").write(wrap(D.boil_face(seed_of(c["name"]) + 1, n, rough=2.2, **kw2)))

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

    # empty-state scene: alice asks, bob answers. faces boil; arrow, words, bubbles and stamp are still
    W, H = 960, 300
    a = recipe(data["cast"][0]); b = recipe(data["cast"][1])
    p = Pen(77, 3)
    s = D.place(D.boil_face(101, FRAMES, look=(1.5, 0), **a), 40, 40, 1.5)
    s += D.place(D.boil_face(202, FRAMES, look=(-1.5, 0), **b), 740, 40, 1.5)
    s += D.boil(lambda pen: D.arrow(pen, (250, 140), (730, 140), w=2.2), 303, FRAMES) + D.text(490, 118, "any update?", 24, "hand", D.PENC, "middle")
    s += D.bubble(p, 60, 232, 210, 50, kind="round", to=(132, 192)) + D.text(165, 264, "is the first rant out yet?", 19, "hand", "currentColor", "middle")
    s += D.bubble(p, 690, 232, 240, 50, kind="round", to=(828, 192)) + D.text(810, 264, "still brewing. come back soon.", 19, "hand", "currentColor", "middle")
    s += D.stamp(p, 420, 200, "0 posts", "currentColor", rot=-6, size=13)
    open(os.path.join(OUT, "scenes", "empty-state.svg"), "w").write(wrap(s, f"0 0 {W} {H}"))

    # marks: drawn ui bits that are not people or things. play sits on a video link.
    p = Pen(5, 3, rough=0.7)
    m  = p.fill(D.ell(60, 60, 36, 36, n=30), "var(--paper)", dx=0, dy=0, jitter=1.2, op=.86)
    m += p.line(D.ell(60, 60, 36, 36, n=30), closed=True, w=2.8)
    m += p.fill([(50, 40), (86, 60), (50, 80)], D.WASH["clay"], dx=0, dy=0, jitter=1.2)
    m += p.line([(50, 40), (86, 60), (50, 80)], closed=True, w=2.4)
    open(os.path.join(OUT, "marks", "play.svg"), "w").write(wrap(m))

    # favicon: khaki tile with a speech bubble holding a rant scribble. thick strokes so it survives 16px; no fonts, so it renders the same everywhere
    p = Pen(9, 2, rough=1.0)
    f = p.line(D.ell(60, 54, 42, 30, n=22, sq=3), closed=True, w=6)
    f += p.line([(44, 82), (34, 100), (58, 84)], w=6)
    f += p.line([(34, 50), (42, 40), (50, 60), (58, 40), (66, 60), (74, 40), (82, 60), (88, 50)], w=5, step=30)
    open(os.path.join(ROOT, "assets", "favicon.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="26" fill="#d2c79d"/><g style="color:#171612">' + f + "</g></svg>\n")
    print(f"people {len(people)}×2, things {len(THINGS)}, sprite {len(syms)} symbols, scene, favicon")

if __name__ == "__main__":
    main()
