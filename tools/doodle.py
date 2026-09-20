import math, random

_ID = [0]
def uid(p="c"):
    _ID[0] += 1
    return f"{p}{_ID[0]}"

def resample(pts, step=6.0, closed=False):
    P = list(pts) + ([pts[0]] if closed else [])
    out = [P[0]]
    for a, b in zip(P, P[1:]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        L = math.hypot(dx, dy)
        n = max(1, int(L // step))
        for i in range(1, n+1):
            t = i/n
            out.append((a[0]+dx*t, a[1]+dy*t))
    if closed: out.pop()
    return out

def catmull(pts, closed, t=1.0):
    n = len(pts)
    if n < 2: return ""
    def P(i):
        return pts[i % n] if closed else pts[max(0, min(n-1, i))]
    d = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in (range(n) if closed else range(n-1)):
        p0, p1, p2, p3 = P(i-1), P(i), P(i+1), P(i+2)
        c1 = (p1[0]+(p2[0]-p0[0])/6*t, p1[1]+(p2[1]-p0[1])/6*t)
        c2 = (p2[0]-(p3[0]-p1[0])/6*t, p2[1]-(p3[1]-p1[1])/6*t)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    if closed: d.append("Z")
    return "".join(d)

def ell(cx, cy, rx, ry, n=24, rot=0.0, sq=2.0):
    pts = []
    for i in range(n):
        t = 2*math.pi*i/n
        c, s = math.cos(t), math.sin(t)
        x = rx*math.copysign(abs(c)**(2/sq), c); y = ry*math.copysign(abs(s)**(2/sq), s)
        if rot:
            xr = x*math.cos(rot) - y*math.sin(rot); y = x*math.sin(rot) + y*math.cos(rot); x = xr
        pts.append((cx+x, cy+y))
    return pts

def rect(x, y, w, h):
    return [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]

def arc(cx, cy, r, a0, a1, n=10, ry=None):
    ry = r if ry is None else ry
    return [(cx + r*math.cos(math.radians(a0 + (a1-a0)*i/n)), cy + ry*math.sin(math.radians(a0 + (a1-a0)*i/n))) for i in range(n+1)]

def mv(pts, dx, dy): return [(x+dx, y+dy) for x, y in pts]
def sc(pts, s, cx=60, cy=64): return [(cx+(x-cx)*s, cy+(y-cy)*s) for x, y in pts]

# style: 1 glyph · 2 line · 3 wash · 4 pencil · 5 ink · 6 cut-paper
class Pen:
    def __init__(self, seed=1, style=3, rough=1.0, boil_seed=None, boil=0.35):
        """rough: 0 ruler · 0.5 careful · 1 default · 1.5 quick · 2 shaky · 3 caffeine
        boil_seed: a second random stream that adds `boil` × the wobble on top of the base wobble, so frames drawn
        with the same `seed` and different `boil_seed`s share one drawing and differ only slightly (line boil)."""
        self.r = random.Random(seed); self.style = style; self.rough = rough
        self.r2 = random.Random(boil_seed) if boil_seed is not None else None; self.boil = boil
    @property
    def jit(self): return {1: 0.22, 2: 0.75, 3: 0.75, 4: 0.85, 5: 1.0, 6: 0.8}[self.style] * self.rough
    def _step(self, step): return step if self.rough <= 1.2 else max(3.0, step * (1.2 / self.rough))
    @property
    def fills(self): return self.style >= 3 and self.style != 4
    @property
    def hatches(self): return self.style in (4, 5)
    @property
    def off(self): return {1: (0, 0), 2: (0, 0), 3: (2.2, 1.6), 4: (0, 0), 5: (2.8, 2.2), 6: (5, 4)}[self.style]
    def _j(self, pts, amt):
        out = [(x+self.r.gauss(0, amt), y+self.r.gauss(0, amt)) for x, y in pts]
        if self.r2 is not None and amt > 0:
            b = amt * self.boil
            out = [(x+self.r2.gauss(0, b), y+self.r2.gauss(0, b)) for x, y in out]
        return out
    def line(self, pts, closed=False, w=1.5, color="currentColor", op=1.0, jitter=None, step=6, dbl=None):
        j = self.jit if jitter is None else jitter * max(self.rough, 0.001)
        step = self._step(step) * (2.5 if self.style == 1 else 1)
        P = resample(pts, step, closed) if (j > 0 and len(pts) > 1) else list(pts)
        d = catmull(self._j(P, j) if j > 0 else P, closed)
        o = f' opacity="{op}"' if op < 1 else ""
        s = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{o}></path>'
        dbl = (self.style >= 5) if dbl is None else dbl
        if dbl and j > 0:
            d2 = catmull(self._j(P, j*1.3), closed)
            s += f'<path d="{d2}" fill="none" stroke="{color}" stroke-width="{w*0.65:.2f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.45"></path>'
        return s
    def fill(self, pts, color, dx=None, dy=None, jitter=1.4, op=None, step=8):
        ox, oy = self.off
        dx = ox if dx is None else dx; dy = oy if dy is None else dy
        P = resample(pts, self._step(step), True)
        P = [(x+dx, y+dy) for x, y in self._j(P, jitter * self.rough)]
        o = f' opacity="{op}"' if op is not None else ""
        return f'<path d="{catmull(P, True)}" fill="{color}" stroke="none"{o}></path>'
    def hatch(self, pts, spacing=4.0, angle=50, color="currentColor", w=1.0, op=0.85, cross=False, dx=0, dy=0):
        cid = uid("h")
        P = mv(pts, dx, dy)
        xs = [p[0] for p in P]; ys = [p[1] for p in P]
        x0, x1, y0, y1 = min(xs)-2, max(xs)+2, min(ys)-2, max(ys)+2
        clip = f'<clipPath id="{cid}"><path d="{catmull(resample(P, 8, True), True)}"></path></clipPath>'
        lines = []
        for ang in ([angle, angle+90] if cross else [angle]):
            a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
            cx, cy = (x0+x1)/2, (y0+y1)/2; L = math.hypot(x1-x0, y1-y0)
            k = -L/2
            while k <= L/2:
                px, py = cx - sa*k, cy + ca*k
                lines.append(self.line([(px-ca*L/2, py-sa*L/2), (px+ca*L/2, py+sa*L/2)], w=w, color=color, jitter=0.45, step=10, dbl=False))
                k += spacing + self.r.uniform(-0.5, 0.5)
        return clip + f'<g clip-path="url(#{cid})" opacity="{op}">{"".join(lines)}</g>'
    def scribble(self, pts, density=2.5, color="currentColor", w=1.2, op=0.9):
        cid = uid("s")
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        clip = f'<clipPath id="{cid}"><path d="{catmull(resample(pts, 8, True), True)}"></path></clipPath>'
        path = []
        y = y0
        flip = False
        while y < y1:
            xa, xb = (x0, x1) if not flip else (x1, x0)
            path.append((xa + self.r.uniform(-3, 3), y + self.r.uniform(-1.5, 1.5)))
            path.append((xb + self.r.uniform(-3, 3), y + density/2 + self.r.uniform(-1.5, 1.5)))
            y += density; flip = not flip
        d = catmull(path, False, 0.6)
        return clip + f'<g clip-path="url(#{cid})" opacity="{op}"><path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"></path></g>'
    def speckle(self, pts, n=40, color="currentColor", r=0.7, op=0.5):
        cid = uid("k")
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        clip = f'<clipPath id="{cid}"><path d="{catmull(resample(pts, 8, True), True)}"></path></clipPath>'
        dots = "".join(f'<circle cx="{self.r.uniform(min(xs), max(xs)):.1f}" cy="{self.r.uniform(min(ys), max(ys)):.1f}" r="{r}" fill="{color}"></circle>' for _ in range(n))
        return clip + f'<g clip-path="url(#{cid})" opacity="{op}">{dots}</g>'
    def dot(self, x, y, r=2.2, color="currentColor"):
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"></circle>'
    def shape(self, pts, wash=None, w=1.5, shade=None, color="currentColor", closed=True, hatch_color="currentColor"):
        """wash fill (styles 3,5,6) + optional pencil/ink hatch (4,5) + outline"""
        s = ""
        if wash and self.fills:
            s += self.fill(pts, wash, op=0.85 if self.style != 6 else 0.95)
        if self.style == 4 and wash:
            s += self.hatch(pts, spacing=3.6, angle=62, color=hatch_color if hatch_color != "currentColor" else wash, w=1.1, op=0.95)
        if self.style == 5 and shade:
            s += self.hatch(shade, spacing=3.2, angle=55, w=0.9, op=0.75)
        if self.style == 6:
            s += self.speckle(pts, n=30)
        s += self.line(pts, closed=closed, w=w if self.style != 6 else 1.2, color=color)
        return s

def patch(pen, kind="torn", x=-8, y=-8, w=136, h=136, rot=0.0):
    """khaki paper patch that travels with the doodle so it never inverts on the dark page"""
    cx, cy = x + w/2, y + h/2
    if kind == "blob":
        pts = ell(cx, cy, w/2, h/2, n=22)
        body = pen.fill(pts, "var(--dpaper)", dx=0, dy=0, jitter=2.4, step=9) + pen.line(pts, closed=True, w=1, color="var(--dedge)", jitter=2.2, step=9, dbl=False)
    elif kind == "round":
        pts = ell(cx, cy, w/2, h/2, n=26)
        body = pen.fill(pts, "var(--dpaper)", dx=0, dy=0, jitter=1.4, step=8) + pen.line(pts, closed=True, w=1, color="var(--dedge)", jitter=1.2, step=8, dbl=False)
    else:
        pts = rect(x, y, w, h)
        body = pen.fill(pts, "var(--dpaper)", dx=0, dy=0, jitter=2.2, step=7) + pen.line(pts, closed=True, w=1, color="var(--dedge)", jitter=2.0, step=7, dbl=False)
    if rot:
        return f'<g transform="rotate({rot} {cx} {cy})">{body}</g>'
    return body

def svg(inner, size=120, vb="0 0 120 120", extra="", sticker=None, seed=1, rot=0.0):
    """sticker: None (inherit colour, for inline glyphs) | torn | blob | round"""
    col = "color: var(--ink);"
    if sticker:
        p = Pen(seed, 3)
        inner = patch(p, sticker, rot=rot) + inner
    return f'<svg width="{size}" height="{size}" viewBox="{vb}" aria-hidden="true" style="{col} flex: none; overflow: visible; {extra}">{inner}</svg>'

def scene_patch(pen, W, H, pad=18):
    pts = rect(-pad, -pad, W + 2*pad, H + 2*pad)
    return pen.fill(pts, "var(--dpaper)", dx=0, dy=0, jitter=2.6, step=12) + pen.line(pts, closed=True, w=1, color="var(--dedge)", jitter=2.4, step=12, dbl=False)

def boil(make, seed, n=3, style=3, rough=1.0, amount=0.35):
    """Line boil for one element. make(pen) draws it; it is drawn n times with the same base seed and a different
    boil_seed each, so the frames are one drawing whose line shifts by `amount` of its wobble. The frames go in
    <g class="f fK"> groups that the site's stylesheet shows one at a time. Faces and objects only — arrows, text,
    bubbles and stamps stay still."""
    if n <= 1:
        return make(Pen(seed, style, rough=rough))
    return "".join(f'<g class="f f{k}">{make(Pen(seed, style, rough=rough, boil_seed=seed + 1000 + k*17, boil=amount))}</g>' for k in range(n))

def place(inner, x, y, s=1.0, rot=0):
    r = f" rotate({rot} 60 64)" if rot else ""
    return f'<g transform="translate({x} {y}) scale({s}){r}">{inner}</g>'

# ---------------- palettes ----------------
SKIN = {f"s{i}": f"var(--s{i})" for i in range(1, 10)}
PENCIL = {f"s{i}": f"var(--p{i})" for i in range(1, 10)}
HAIR = {k: f"var(--h-{k})" for k in ("ink", "brown", "auburn", "blond", "gray", "white", "purple", "teal")}
INKF = "var(--h-ink)"
CHEEK = "var(--cheek)"
WASH = {"sage": "var(--w-sage)", "blue": "var(--w-blue)", "ochre": "var(--w-ochre)", "mauve": "var(--w-mauve)", "clay": "var(--w-clay)", "gray": "var(--w-gray)"}
PAPER = "var(--paper)"
PENC = "var(--pen)"
RED = "var(--red)"
GREEN = "var(--green)"

HEADS = {
    "round": dict(rx=27, ry=30, sq=2.0, taper=0.0),
    "long": dict(rx=23, ry=34, sq=2.0, taper=0.06),
    "square": dict(rx=26, ry=31, sq=3.4, taper=0.0),
    "wide": dict(rx=31, ry=27, sq=2.2, taper=0.0),
    "egg": dict(rx=27, ry=31, sq=2.0, taper=0.24),
    "heart": dict(rx=28, ry=30, sq=2.3, taper=0.38),
    "block": dict(rx=25, ry=34, sq=3.0, taper=0.0),
    "small": dict(rx=23, ry=26, sq=2.0, taper=0.1),
}
def head_pts(kind, cx=60, cy=64, n=30):
    h = HEADS[kind]; pts = []
    for i in range(n):
        t = 2*math.pi*i/n; c, s = math.cos(t), math.sin(t)
        x = h["rx"]*math.copysign(abs(c)**(2/h["sq"]), c); y = h["ry"]*math.copysign(abs(s)**(2/h["sq"]), s)
        if s > 0: x *= (1 - h["taper"]*s)
        pts.append((cx+x, cy+y))
    return pts

# ---------------- backings ----------------
BLOBS = {
    "blob": [(60, 6), (92, 12), (110, 40), (112, 70), (100, 104), (66, 116), (30, 108), (8, 78), (8, 42), (28, 14)],
    "blob2": [(22, 20), (60, 8), (100, 18), (114, 52), (106, 92), (72, 114), (34, 110), (8, 84), (6, 48)],
    "square": [(14, 12), (106, 12), (110, 108), (12, 110)],
    "tall": [(30, 4), (90, 4), (100, 60), (92, 118), (28, 118), (18, 60)],
}
def backing(pen, kind, wash, rot=0):
    if not kind or kind == "none": return ""
    col = WASH.get(wash, wash)
    if kind == "ring":
        return pen.line(ell(60, 64, 54, 52, n=28), closed=True, w=3.5, color=col, jitter=1.2, dbl=False)
    if kind == "hatch":
        return pen.hatch(ell(60, 62, 56, 56), spacing=6, angle=60, color=col, w=2.4, op=1)
    if kind == "scribble":
        return pen.scribble(ell(60, 62, 54, 54), density=4, color=col, w=2.2, op=1)
    pts = BLOBS[kind]
    if rot: pts = [(60+(x-60)*math.cos(rot)-(y-60)*math.sin(rot), 60+(x-60)*math.sin(rot)+(y-60)*math.cos(rot)) for x, y in pts]
    return pen.fill(pts, col, dx=0, dy=0, jitter=1.6)

# ---------------- face parts ----------------
def eyes(pen, kind, look=(0, 0), skin=None):
    L, R = (49, 58), (71, 58); lx, ly = look
    paper = PAPER
    o = ""
    if kind == "dot":
        o += pen.dot(L[0]+lx, L[1]+ly) + pen.dot(R[0]+lx, R[1]+ly)
    elif kind == "oval":
        for cx, cy in (L, R):
            o += pen.line(ell(cx, cy, 5, 3.3, n=12), closed=True, w=1.4) + pen.dot(cx+lx+0.5, cy+ly, 1.8)
    elif kind == "wide":
        for cx, cy in (L, R):
            o += pen.fill(ell(cx, cy, 6.5, 6.5, n=14), paper, dx=0, dy=0, jitter=0.4) + pen.line(ell(cx, cy, 6.5, 6.5, n=14), closed=True, w=1.4) + pen.dot(cx+lx, cy+ly+0.5, 2.6)
    elif kind == "closed":
        for cx, cy in (L, R): o += pen.line([(cx-5, cy), (cx, cy+3), (cx+5, cy)], w=1.5)
    elif kind == "sleepy":
        for cx, cy in (L, R): o += pen.line([(cx-5, cy+1), (cx+5, cy+1)], w=1.6)
    elif kind == "wink":
        o += pen.line(ell(L[0], L[1], 5, 3.3, n=12), closed=True, w=1.4) + pen.dot(L[0]+lx, L[1], 1.8) + pen.line([(R[0]-5, R[1]), (R[0], R[1]+3), (R[0]+5, R[1])], w=1.5)
    elif kind == "line":
        for cx, cy in (L, R): o += pen.line([(cx-6, cy+1), (cx, cy-1.5), (cx+6, cy+1)], w=1.6) + pen.dot(cx+lx, cy+1.2, 1.5)
    elif kind == "hooded":
        for cx, cy in (L, R): o += pen.line(ell(cx, cy, 5, 3, n=12), closed=True, w=1.3) + pen.dot(cx+lx, cy+ly, 1.7) + pen.line([(cx-7, cy-3), (cx, cy-5.5), (cx+7, cy-3)], w=1.4)
    elif kind == "glasses":
        for cx, cy in (L, R): o += pen.line(ell(cx, cy, 8.5, 8.5, n=16), closed=True, w=1.4) + pen.dot(cx+lx+1, cy+ly, 1.8)
        o += pen.line([(57.5, 58), (62.5, 58)], w=1.4) + pen.line([(40.5, 57), (34, 54)], w=1.4) + pen.line([(79.5, 57), (86, 54)], w=1.4)
    elif kind == "glasses-sq":
        for cx, cy in (L, R): o += pen.line(ell(cx, cy, 8.5, 6.5, n=16, sq=3.5), closed=True, w=1.4) + pen.dot(cx+lx+1, cy+ly, 1.8)
        o += pen.line([(57.5, 57), (62.5, 57)], w=1.4) + pen.line([(40.5, 56), (34, 53)], w=1.4) + pen.line([(79.5, 56), (86, 53)], w=1.4)
    elif kind == "shades":
        for cx, cy in (L, R): o += pen.fill(ell(cx, cy, 9, 6.5, n=16, sq=3), INKF, dx=0, dy=0, jitter=0.5) + pen.line(ell(cx, cy, 9, 6.5, n=16, sq=3), closed=True, w=1.2)
        o += pen.line([(58, 56), (62, 56)], w=1.6) + pen.line([(40, 55), (34, 52)], w=1.4) + pen.line([(80, 55), (86, 52)], w=1.4)
    elif kind == "patch":
        o += pen.line(ell(L[0], L[1], 5, 3.3, n=12), closed=True, w=1.4) + pen.dot(L[0]+lx, L[1], 1.8)
        o += pen.fill(ell(R[0], R[1], 8, 7, n=14), INKF, dx=0, dy=0, jitter=0.5) + pen.line(ell(R[0], R[1], 8, 7, n=14), closed=True, w=1.2) + pen.line([(63, 52), (40, 44)], w=1.3) + pen.line([(79, 52), (87, 46)], w=1.3)
    elif kind == "mask":
        m = [(38, 52), (60, 48), (82, 52), (84, 60), (82, 68), (60, 71), (38, 68), (36, 60)]
        o += pen.fill(m, INKF, dx=0, dy=0, jitter=0.6) + pen.line(m, closed=True, w=1.2)
        for cx, cy in (L, R): o += pen.fill(ell(cx, cy+1, 5.5, 4, n=12), paper, dx=0, dy=0, jitter=0.3) + pen.dot(cx+lx, cy+1, 2, "currentColor")
    elif kind == "x":
        for cx, cy in (L, R): o += pen.line([(cx-4, cy-4), (cx+4, cy+4)], w=1.6) + pen.line([(cx+4, cy-4), (cx-4, cy+4)], w=1.6)
    elif kind == "spiral":
        for cx, cy in (L, R):
            pts = [(cx + (i*0.5)*math.cos(i*0.9), cy + (i*0.5)*math.sin(i*0.9)) for i in range(0, 14)]
            o += pen.line(pts, w=1.3, jitter=0.2)
    elif kind == "squint":
        for cx, cy in (L, R): o += pen.line([(cx-5, cy-1), (cx, cy+1), (cx+5, cy-1)], w=1.6)
    elif kind == "monocle":
        o += pen.line(ell(L[0], L[1], 5, 3.3, n=12), closed=True, w=1.4) + pen.dot(L[0]+lx, L[1], 1.8)
        o += pen.line(ell(R[0], R[1], 9, 9, n=16), closed=True, w=1.5) + pen.dot(R[0]+lx, R[1]+ly, 1.8) + pen.line([(78, 65), (84, 80), (82, 92)], w=1.1)
    return o

def brows(pen, kind, y=48):
    L = [(43, y), (49, y-3), (55, y)]; R = [(65, y), (71, y-3), (77, y)]
    if kind == "none": return ""
    if kind == "flat": return pen.line([(43, y), (55, y-1)], w=1.5) + pen.line([(65, y-1), (77, y)], w=1.5)
    if kind == "arch": return pen.line(L, w=1.5) + pen.line(R, w=1.5)
    if kind == "raised": return pen.line(mv(L, 0, -4), w=1.5) + pen.line(mv(R, 0, -4), w=1.5)
    if kind == "one-up": return pen.line([(43, y), (55, y-1)], w=1.5) + pen.line(mv(R, 0, -5), w=1.5)
    if kind == "angry": return pen.line([(43, y-4), (55, y+2)], w=1.8) + pen.line([(65, y+2), (77, y-4)], w=1.8)
    if kind == "worried": return pen.line([(43, y+1), (55, y-4)], w=1.5) + pen.line([(65, y-4), (77, y+1)], w=1.5)
    if kind == "uni": return pen.line([(43, y), (52, y-3), (60, y), (68, y-3), (77, y)], w=1.6)
    if kind == "thick":
        return pen.fill([(42, y+1), (56, y-3), (56, y+1), (43, y+3)], "currentColor", dx=0, dy=0, jitter=0.4) + pen.fill([(64, y+1), (78, y-3), (77, y+3), (64, y+1)], "currentColor", dx=0, dy=0, jitter=0.4)
    return ""

def nose(pen, kind):
    if kind == "l": return pen.line([(61, 56), (59, 63), (57, 70), (63, 71)], w=1.5)
    if kind == "hook": return pen.line([(60, 55), (64, 62), (63, 70), (57, 70)], w=1.5)
    if kind == "button": return pen.line([(56, 69), (60, 72), (64, 69)], w=1.5)
    if kind == "wide": return pen.line([(54, 66), (55, 71), (60, 73), (65, 71), (66, 66)], w=1.5)
    if kind == "long": return pen.line([(61, 54), (60, 64), (58, 75), (64, 75)], w=1.5)
    if kind == "dot": return pen.dot(60, 69, 1.6)
    if kind == "line": return pen.line([(60, 56), (58, 71)], w=1.5)
    if kind == "up": return pen.line([(58, 58), (56, 68), (60, 71), (65, 68)], w=1.5)
    return ""

def mouth(pen, kind, teeth=False):
    if kind == "smile": return pen.line([(53, 85), (60, 88.5), (67, 85)], w=1.5)
    if kind == "big":
        return pen.fill([(50, 84), (60, 92), (70, 84)], PAPER, dx=0, dy=0, jitter=0.4) + pen.line([(50, 84), (60, 92), (70, 84)], closed=True, w=1.5) + pen.line([(54, 85), (66, 85)], w=1.1)
    if kind == "flat": return pen.line([(54, 86), (66, 86)], w=1.5)
    if kind == "o": return pen.line(ell(60, 87, 3, 2.6, n=10), closed=True, w=1.4)
    if kind == "grin": return pen.line([(52, 84), (60, 89), (68, 84)], w=1.5) + pen.line([(56, 85), (56, 88)], w=1.1) + pen.line([(60, 86), (60, 89)], w=1.1) + pen.line([(64, 85), (64, 88)], w=1.1)
    if kind == "frown": return pen.line([(53, 89), (60, 85), (67, 89)], w=1.5)
    if kind == "smirk": return pen.line([(54, 87), (62, 87.5), (68, 83)], w=1.5)
    if kind == "shout": return pen.fill(ell(60, 89, 6.5, 6, n=12), INKF, dx=0, dy=0, jitter=0.4) + pen.line(ell(60, 89, 6.5, 6, n=12), closed=True, w=1.2)
    if kind == "wavy": return pen.line([(52, 86), (56, 84), (60, 87.5), (64, 84), (68, 86)], w=1.5)
    if kind == "tongue": return pen.line([(53, 85), (60, 88.5), (67, 85)], w=1.5) + pen.fill(ell(62, 91, 3, 3.2, n=10), "#c98f7a", dx=0, dy=0, jitter=0.3) + pen.line(ell(62, 91, 3, 3.2, n=10), closed=True, w=1.1)
    if kind == "grit": return pen.line(rect(52, 84, 16, 6), closed=True, w=1.4) + "".join(pen.line([(x, 84), (x, 90)], w=1) for x in (56, 60, 64))
    if kind == "pout": return pen.line([(56, 86), (60, 84.5), (64, 86)], w=1.6)
    if kind == "sad-open": return pen.line(ell(60, 89, 4, 3, n=10), closed=True, w=1.4) + pen.line([(52, 92), (55, 88)], w=1.2) + pen.line([(68, 92), (65, 88)], w=1.2)
    return ""

def facial(pen, kind, color="currentColor"):
    if not kind or kind == "none": return ""
    if kind == "stubble":
        return "".join(pen.dot(x, y, 0.8) for x, y in [(46, 84), (50, 90), (55, 95), (60, 97), (66, 95), (71, 90), (75, 84), (48, 78), (73, 78), (63, 92), (57, 92)])
    if kind == "hatch":
        return "".join(pen.line([(44+i*4, 88+(2 if i % 2 else 0)), (43+i*4, 97)], w=1.2, dbl=False) for i in range(9))
    if kind == "full":
        b = [(34, 70), (40, 96), (50, 106), (60, 109), (70, 106), (80, 96), (86, 70), (82, 82), (74, 92), (60, 96), (46, 92), (38, 82)]
        s = pen.fill(b, color, dx=0, dy=0, jitter=1.0, op=0.9) if pen.fills else ""
        if pen.style == 4: s += pen.hatch(b, spacing=3, angle=80, w=1)
        return s + pen.line(b, closed=True, w=1.4)
    if kind == "goatee":
        g = [(54, 92), (66, 92), (65, 102), (60, 105), (55, 102)]
        s = pen.fill(g, color, dx=0, dy=0, jitter=0.6) if pen.fills else pen.hatch(g, spacing=2.5, angle=80, w=1)
        return s + pen.line(g, closed=True, w=1.2)
    if kind == "mustache": return pen.line([(50, 80), (56, 77), (60, 80)], w=1.8) + pen.line([(60, 80), (64, 77), (70, 80)], w=1.8)
    if kind == "handlebar": return pen.line([(48, 82), (54, 77), (60, 80)], w=1.8) + pen.line([(60, 80), (66, 77), (72, 82), (70, 86)], w=1.8) + pen.line([(48, 82), (50, 86)], w=1.6)
    if kind == "patch": return pen.line([(58, 92), (60, 96), (62, 92)], w=1.6)
    if kind == "big":
        b = [(30, 62), (36, 100), (48, 114), (60, 117), (72, 114), (84, 100), (90, 62), (86, 78), (78, 92), (60, 97), (42, 92), (34, 78)]
        s = pen.fill(b, color, dx=0, dy=0, jitter=1.2, op=0.9) if pen.fills else ""
        s += pen.hatch(b, spacing=3.2, angle=75, w=1, op=0.8) if pen.style in (4, 5) else ""
        return s + pen.line(b, closed=True, w=1.4) + pen.line([(52, 84), (60, 88), (68, 84)], w=1.4)
    return ""

CAP = [(34, 58), (36, 44), (46, 34), (60, 31), (74, 34), (84, 44), (86, 58), (78, 48), (60, 44), (42, 48)]
def hair(pen, kind, color="ink", wash="sage"):
    """returns (behind, front)"""
    col = HAIR.get(color, color); wc = WASH.get(wash, wash)
    def solid(pts, c=col, hatch=True, w=1.4):
        s = ""
        if pen.fills: s += pen.fill(pts, c, jitter=1.0, op=0.92)
        if pen.style in (4, 5) and hatch: s += pen.hatch(pts, spacing=2.8, angle=70, w=1.1, op=0.8, color="currentColor")
        if pen.style == 2: s += pen.hatch(pts, spacing=4.5, angle=70, w=1.0, op=0.8)
        if pen.style == 1: pass
        return s + pen.line(pts, closed=True, w=w)
    B, F = "", ""
    if kind in ("none", "bald"):
        F = pen.line([(48, 40), (54, 36)], w=1.2) if pen.style >= 2 else ""
    elif kind == "short": F = solid(CAP)
    elif kind == "side":
        F = solid([(34, 58), (38, 42), (52, 32), (70, 32), (84, 42), (86, 58), (84, 52), (72, 42), (56, 46), (40, 54)]) + pen.line([(42, 52), (60, 44), (78, 42)], w=1.3)
    elif kind == "fringe": F = solid([(34, 60), (36, 42), (48, 32), (72, 32), (84, 42), (86, 60), (84, 52), (60, 53), (36, 52)])
    elif kind == "bun": F = solid(CAP) + solid(ell(60, 28, 8, 7, n=12))
    elif kind == "ponytail": B = solid([(84, 42), (98, 50), (101, 70), (94, 84), (90, 70), (86, 54)]); F = solid(CAP)
    elif kind == "afro":
        big = ell(60, 50, 42, 38, n=26)
        B = (pen.fill(big, col, jitter=2.0, op=0.95) if pen.fills else "") + (pen.scribble(big, density=3, w=1.2, op=0.9) if pen.style in (2, 4, 5) else "") + pen.line(big, closed=True, w=1.5, jitter=1.8)
    elif kind == "coils":
        big = ell(60, 50, 38, 32, n=24)
        B = (pen.fill(big, col, jitter=1.5, op=0.95) if pen.fills else "") + pen.line(big, closed=True, w=1.4)
        F = "".join(pen.line(ell(60+34*math.cos(a), 50+29*math.sin(a), 3.5, 3.5, n=8), closed=True, w=1.1) for a in [math.radians(180+i*13) for i in range(15)])
    elif kind == "locs":
        F = solid(CAP)
        for i, x in enumerate([32, 37, 42, 78, 83, 88]):
            F += pen.line([(x, 52+i % 3*2), (x-2+(i % 2)*4, 72), (x+1, 96)], w=3.2 if pen.fills else 2.2, color=col if pen.fills else "currentColor", dbl=False)
            F += pen.line([(x, 52+i % 3*2), (x-2+(i % 2)*4, 72), (x+1, 96)], w=1.0, dbl=False)
    elif kind == "braids":
        F = solid(CAP)
        for x in (31, 89):
            for y in range(58, 104, 9):
                F += (pen.fill(ell(x, y, 4, 5.5, n=10), col, dx=0, dy=0, jitter=0.4, op=0.9) if pen.fills else "") + pen.line(ell(x, y, 4, 5.5, n=10), closed=True, w=1.1)
    elif kind == "cornrows":
        F = pen.line(CAP, closed=True, w=1.4)
        for dx in (-14, -7, 0, 7, 14):
            F += pen.line([(60+dx*1.6, 48), (60+dx*1.3, 38), (60+dx*0.9, 33)], w=1.3, dbl=False)
    elif kind == "receding":
        F = solid([(34, 62), (35, 48), (44, 42), (46, 50), (38, 60)], hatch=True) + solid([(86, 62), (85, 48), (76, 42), (74, 50), (82, 60)], hatch=True)
    elif kind == "long":
        B = solid([(30, 50), (34, 34), (60, 26), (86, 34), (90, 50), (94, 100), (86, 112), (34, 112), (26, 100)])
        B += pen.line([(36, 60), (34, 90), (36, 108)], w=1.1) + pen.line([(84, 60), (86, 90), (84, 108)], w=1.1)
        F = pen.line([(38, 50), (54, 40), (78, 42)], w=1.3)
    elif kind == "wavy":
        B = solid([(30, 50), (34, 34), (60, 26), (86, 34), (90, 50), (96, 80), (90, 112), (30, 112), (24, 80)])
        for x in (36, 84):
            B += pen.line([(x, 56), (x-4, 70), (x+3, 84), (x-3, 98), (x+2, 108)], w=1.1)
        F = pen.line([(36, 52), (52, 40), (74, 40), (86, 50)], w=1.3)
    elif kind == "curly":
        F = solid([(34, 56), (36, 40), (48, 30), (72, 30), (84, 40), (86, 56), (80, 46), (60, 44), (40, 46)], hatch=False)
        for a in range(6):
            cx = 38 + a*9; F += pen.line(arc(cx, 42-abs(a-2.5)*3, 5.5, 200, 340, n=6), w=1.3)
    elif kind == "spiky":
        F = solid([(34, 54), (40, 30), (46, 44), (52, 24), (58, 42), (64, 22), (70, 42), (76, 28), (82, 46), (86, 54), (60, 48)])
    elif kind == "mohawk":
        F = solid([(52, 42), (54, 18), (60, 6), (66, 18), (68, 42), (60, 46)]) + pen.line([(38, 46), (50, 44)], w=1.2) + pen.line([(70, 44), (82, 46)], w=1.2)
    elif kind == "hijab":
        big = [(26, 52), (32, 32), (60, 20), (88, 32), (94, 52), (98, 84), (102, 118), (18, 118), (22, 84)]
        B = (pen.fill(big, wc, jitter=1.4) if pen.fills else "") + pen.line(big, closed=True, w=1.5)
        inner = [(38, 60), (38, 44), (60, 32), (82, 44), (82, 60), (86, 96), (78, 110)]
        F = pen.line(inner, w=1.4) + pen.line([(38, 60), (36, 90), (42, 110)], w=1.4) + pen.line([(84, 70), (92, 96)], w=1.0) + pen.line([(30, 70), (24, 100)], w=1.0)
    elif kind == "turban":
        t = [(32, 54), (36, 34), (48, 22), (60, 18), (72, 22), (84, 34), (88, 54), (74, 44), (60, 42), (46, 44)]
        F = (pen.fill(t, wc, jitter=1.2) if pen.fills else "") + pen.line(t, closed=True, w=1.5) + pen.line([(40, 34), (60, 24), (78, 34)], w=1.1) + pen.line([(36, 46), (66, 26)], w=1.1) + pen.line([(50, 50), (84, 34)], w=1.1)
    elif kind == "kufi":
        k = [(36, 50), (38, 32), (82, 32), (84, 50), (60, 46)]
        F = (pen.fill(k, wc, jitter=1.0) if pen.fills else "") + pen.line(k, closed=True, w=1.5) + pen.line([(38, 40), (82, 40)], w=1.0) + "".join(pen.dot(x, 36, 1) for x in range(44, 80, 6))
    elif kind == "headwrap":
        w_ = [(34, 54), (36, 30), (46, 14), (60, 10), (74, 14), (84, 30), (86, 54), (60, 46)]
        F = (pen.fill(w_, wc, jitter=1.2) if pen.fills else "") + pen.line(w_, closed=True, w=1.5) + pen.line([(40, 34), (60, 22), (80, 34)], w=1.1) + pen.line([(38, 46), (62, 30)], w=1.1)
        F += pen.line(ell(40, 16, 7, 5, n=10, rot=-0.6), closed=True, w=1.3) + pen.line(ell(48, 10, 6, 4, n=10, rot=0.5), closed=True, w=1.3)
    elif kind == "beanie":
        b = [(34, 52), (37, 34), (60, 26), (83, 34), (86, 52), (60, 46)]
        F = solid(b, hatch=False) + solid([(34, 52), (60, 46), (86, 52), (86, 58), (60, 52), (34, 58)], hatch=False) + pen.line([(60, 26), (60, 20)], w=1.3) + pen.line(ell(60, 17, 3.5, 3.5, n=8), closed=True, w=1.2)
    elif kind == "flatcap":
        F = solid([(32, 50), (36, 34), (60, 28), (84, 34), (88, 50), (60, 44)], hatch=False) + solid([(56, 50), (96, 50), (94, 57), (56, 55)], hatch=False)
    elif kind == "bucket":
        F = solid([(38, 46), (40, 30), (60, 26), (80, 30), (82, 46), (60, 42)], hatch=False) + solid([(26, 50), (38, 46), (82, 46), (94, 50), (90, 57), (30, 57)], hatch=False)
    elif kind == "hoodie":
        big = [(18, 62), (28, 34), (60, 18), (92, 34), (102, 62), (108, 118), (12, 118)]
        B = (pen.fill(big, wc, jitter=1.6) if pen.fills else "") + pen.line(big, closed=True, w=1.5)
        F = pen.line([(36, 62), (36, 44), (60, 30), (84, 44), (84, 62), (88, 100), (80, 118)], w=1.4) + pen.line([(36, 62), (32, 100), (40, 118)], w=1.4) + pen.line([(52, 112), (52, 118)], w=1.1) + pen.line([(68, 112), (68, 118)], w=1.1)
    elif kind == "headband":
        F = solid(CAP, hatch=False)
        hb = [(33, 50), (87, 50), (87, 56), (33, 56)]
        F += (pen.fill(hb, wc, dx=0, dy=0, jitter=0.5) if pen.fills else "") + pen.line(hb, closed=True, w=1.3)
    elif kind == "gray":
        F = solid(CAP, c=HAIR["gray"])
    elif kind == "cowlick":
        F = solid(CAP, hatch=False) + pen.line([(64, 32), (70, 22), (74, 26)], w=1.4)
    elif kind == "pigtails":
        F = solid(CAP, hatch=False)
        for x, d in ((28, -1), (92, 1)):
            F += solid(ell(x, 58, 6, 9, n=12, rot=0.4*d), hatch=False)
    elif kind == "topknot":
        F = solid([(34, 58), (36, 44), (46, 34), (60, 31), (74, 34), (84, 44), (86, 58), (78, 48), (60, 44), (42, 48)], hatch=False) + solid(ell(60, 24, 6, 8, n=10), hatch=False)
    elif kind == "helmet":
        h = [(32, 58), (36, 34), (60, 24), (84, 34), (88, 58), (86, 66), (34, 66)]
        F = (pen.fill(h, wc, jitter=1.0) if pen.fills else "") + pen.line(h, closed=True, w=1.6) + pen.line([(34, 60), (86, 60)], w=1.2) + pen.line([(60, 26), (60, 58)], w=1.0)
    return B, F

def extras(pen, kinds, color="currentColor"):
    o = ""
    for k in kinds:
        if k == "blush": o += pen.dot(46, 74, 4.2, CHEEK) + pen.dot(76, 74, 4.2, CHEEK)
        elif k == "freckles": o += "".join(pen.dot(x, y, 0.9) for x, y in [(42, 72), (46, 76), (50, 72), (70, 72), (74, 76), (78, 72), (44, 68), (76, 68)])
        elif k == "mole": o += pen.dot(70, 78, 1.4)
        elif k == "wrinkles": o += pen.line([(36, 56), (40, 58)], w=1) + pen.line([(84, 56), (80, 58)], w=1) + pen.line([(36, 62), (41, 62)], w=1) + pen.line([(84, 62), (79, 62)], w=1) + pen.line([(46, 40), (74, 40)], w=1) + pen.line([(48, 45), (72, 45)], w=1) + pen.line([(48, 80), (46, 90)], w=1) + pen.line([(72, 80), (74, 90)], w=1)
        elif k == "sweat":
            d = [(88, 44), (92, 52), (88, 56), (84, 52)]
            o += pen.fill(d, PAPER, dx=0, dy=0, jitter=0.3) + pen.line(d, closed=True, w=1.3) + pen.line([(94, 60), (97, 66), (94, 68), (91, 66)], closed=True, w=1.2)
        elif k == "tears": o += pen.line([(50, 64), (49, 72), (51, 76)], w=1.3) + pen.line([(72, 64), (73, 72), (71, 76)], w=1.3)
        elif k == "motion": o += pen.line([(22, 52), (16, 50)], w=1.4) + pen.line([(22, 62), (14, 62)], w=1.4) + pen.line([(22, 72), (16, 74)], w=1.4) + pen.line([(98, 52), (104, 50)], w=1.4) + pen.line([(98, 62), (106, 62)], w=1.4) + pen.line([(98, 72), (104, 74)], w=1.4)
        elif k == "cloud":
            c = ell(92, 22, 20, 14, n=18)
            o += pen.scribble(c, density=2.2, w=1.3, op=0.95) + pen.line(c, closed=True, w=1.2, jitter=2.2)
        elif k == "zzz": o += f'<text x="90" y="30" font-family="Caveat, cursive" font-size="22" fill="currentColor" transform="rotate(-12 90 30)">z z z</text>'
        elif k == "q": o += f'<text x="86" y="34" font-family="Caveat, cursive" font-size="34" font-weight="600" fill="{PENC}" transform="rotate(10 86 34)">?</text>'
        elif k == "bang": o += f'<text x="88" y="34" font-family="Caveat, cursive" font-size="36" font-weight="600" fill="{PENC}" transform="rotate(8 88 34)">!</text>'
        elif k == "bangs": o += f'<text x="84" y="34" font-family="Caveat, cursive" font-size="34" font-weight="600" fill="{RED}" transform="rotate(8 84 34)">!!</text>'
        elif k == "stars":
            for (x, y, s) in [(20, 30, 5), (100, 26, 4), (98, 96, 3.5)]:
                o += pen.line([(x-s, y), (x+s, y)], w=1.3) + pen.line([(x, y-s), (x, y+s)], w=1.3)
        elif k == "spark":
            for (x, y) in [(24, 30), (96, 24), (22, 92)]:
                o += pen.line([(x-3, y-3), (x+3, y+3)], w=1.2) + pen.line([(x+3, y-3), (x-3, y+3)], w=1.2)
        elif k == "steam":
            for x in (44, 60, 76): o += pen.line([(x, 28), (x-3, 20), (x+2, 12), (x-2, 6)], w=1.2)
        elif k == "halo": o += pen.line(ell(60, 22, 20, 5, n=18), closed=True, w=1.8, color=PENC)
        elif k == "hearts": o += f'<text x="90" y="34" font-family="Caveat, cursive" font-size="26" fill="{RED}" transform="rotate(12 90 34)">♥</text>'
        elif k == "dots": o += f'<text x="86" y="36" font-family="Caveat, cursive" font-size="28" font-weight="600" fill="currentColor">…</text>'
        elif k == "bandage": o += pen.line(rect(68, 74, 12, 6), closed=True, w=1.2) + pen.line([(72, 74), (72, 80)], w=1) + pen.line([(76, 74), (76, 80)], w=1)
        elif k == "bindi": o += pen.dot(60, 48, 1.8, RED)
        elif k == "nosering": o += pen.line(arc(58, 71, 3, 20, 200, n=8), w=1.3)
        elif k == "earrings": o += pen.line(ell(35, 82, 3.2, 3.2, n=8), closed=True, w=1.3) + pen.line(ell(85, 82, 3.2, 3.2, n=8), closed=True, w=1.3)
        elif k == "studs": o += pen.dot(34, 78, 1.6) + pen.dot(86, 78, 1.6)
        elif k == "ears": o += pen.line(arc(33, 68, 5, 100, 260, n=6, ry=7), w=1.4) + pen.line(arc(87, 68, 5, -80, 80, n=6, ry=7), w=1.4)
        elif k == "headphones": o += pen.line(arc(60, 60, 34, 200, 340, n=12, ry=32), w=2.2) + pen.fill(ell(31, 66, 5, 8, n=10), INKF, dx=0, dy=0, jitter=0.4) + pen.line(ell(31, 66, 5, 8, n=10), closed=True, w=1.2) + pen.fill(ell(89, 66, 5, 8, n=10), INKF, dx=0, dy=0, jitter=0.4) + pen.line(ell(89, 66, 5, 8, n=10), closed=True, w=1.2)
        elif k == "earbud": o += pen.dot(86, 68, 2.4) + pen.line([(86, 70), (86, 80)], w=1.2)
        elif k == "bowtie": o += pen.fill([(48, 106), (60, 111), (72, 106), (72, 117), (60, 112), (48, 117)], "var(--w-blue)", dx=0, dy=0, jitter=0.5) + pen.line([(48, 106), (60, 111), (72, 106), (72, 117), (60, 112), (48, 117)], closed=True, w=1.3)
        elif k == "tie": o += pen.line([(56, 100), (64, 100), (66, 106), (62, 120), (58, 120), (54, 106)], closed=True, w=1.3) + pen.line([(56, 100), (60, 104), (64, 100)], w=1.1)
        elif k == "collar": o += pen.line([(40, 104), (52, 112), (60, 100), (68, 112), (80, 104)], w=1.4)
        elif k == "scarf":
            s_ = [(36, 100), (84, 100), (88, 110), (34, 110)]
            o += (pen.fill(s_, "var(--w-clay)", dx=0, dy=0, jitter=0.6) if pen.fills else "") + pen.line(s_, closed=True, w=1.3) + pen.line([(78, 110), (82, 120)], w=1.3) + pen.line([(72, 110), (74, 120)], w=1.3)
        elif k == "collar-round": o += pen.line(arc(60, 98, 22, 20, 160, n=10, ry=12), w=1.4)
        elif k == "shirt":
            sh = [(30, 118), (36, 102), (50, 98), (60, 106), (70, 98), (84, 102), (90, 118)]
            o += (pen.fill(sh, "var(--w-sage)", dx=0, dy=0, jitter=0.6) if pen.fills else "") + pen.line(sh, w=1.4)
        elif k == "lanyard": o += pen.line([(50, 100), (54, 118)], w=1.1) + pen.line([(70, 100), (66, 118)], w=1.1)
        elif k == "sprout": o += pen.line([(60, 33), (62, 24), (66, 18)], w=1.3) + pen.line(ell(70, 16, 5, 3, n=8, rot=-0.5), closed=True, w=1.2)
        elif k == "antenna": o += pen.line([(60, 33), (60, 18)], w=1.3) + pen.line(ell(60, 14, 3.5, 3.5, n=8), closed=True, w=1.2) + pen.line([(52, 8), (48, 4)], w=1) + pen.line([(68, 8), (72, 4)], w=1)
        elif k == "dizzy": o += pen.line([(60+18*math.cos(a), 30+7*math.sin(a)) for a in [math.radians(i*20) for i in range(19)]], w=1.2, color=PENC) + "".join(pen.dot(60+18*math.cos(a), 30+7*math.sin(a), 2, PENC) for a in [0.4, 2.5, 4.6])
    return o

def face(pen, head="round", skin="s4", hair_="short", hair_color="ink", eye="oval", brow="flat", nose_="l", mouth_="smile", fh=None, extra=(), wash="sage", back="blob", look=(0, 0), back_rot=0, fh_color=None):
    o = backing(pen, back, wash, back_rot)
    B, F = hair(pen, hair_, hair_color, wash if wash else "sage")
    o += B
    H = head_pts(head)
    skin_hex = SKIN.get(skin, skin) if skin else None
    if skin_hex:
        if pen.fills:
            o += pen.fill(H, skin_hex, op=0.88 if pen.style != 6 else 0.95)
        if pen.style == 4:
            o += pen.hatch(H, spacing=3.4, angle=62, color=PENCIL.get(skin, skin_hex), w=1.2, op=0.95)
        if pen.style == 5:
            shade = [p for p in H if p[0] > 60] ; 
            o += pen.hatch([(60, 34), (88, 40), (90, 70), (84, 92), (60, 96)], spacing=3.2, angle=55, w=0.9, op=0.7)
        if pen.style == 6:
            o += pen.speckle(H, n=36, r=0.75, op=0.45)
    if pen.style >= 2 or True:
        o += pen.line(H, closed=True, w=1.5 if pen.style != 6 else 1.2)
    if pen.style >= 2 and hair_ not in ("hijab", "hoodie", "helmet", "turban", "headwrap"):
        o += extras(pen, ["ears"])
    o += F
    o += brows(pen, brow)
    o += eyes(pen, eye, look)
    o += nose(pen, nose_)
    o += mouth(pen, mouth_)
    o += facial(pen, fh, HAIR.get(fh_color or hair_color, HAIR.get(hair_color, "currentColor")))
    if pen.style >= 2:
        o += extras(pen, extra)
    return o

# ---------------- objects ----------------
def obj(pen, kind, wash="blue"):
    wc = WASH.get(wash, wash); S = pen.shape; L = pen.line
    o = ""
    if kind == "envelope":
        o = S(rect(18, 36, 84, 54), wc) + L([(18, 36), (60, 72), (102, 36)], w=1.5) + L([(18, 90), (48, 62)], w=1.2) + L([(102, 90), (72, 62)], w=1.2)
    elif kind == "sealed":
        o = S(rect(18, 36, 84, 54), wc) + L([(18, 36), (60, 72), (102, 36)], w=1.5) + S(ell(60, 70, 8, 8, n=12), "var(--w-clay)") + L([(56, 70), (64, 70)], w=1.2) + L([(60, 66), (60, 74)], w=1.2)
    elif kind == "key":
        o = S(ell(34, 60, 15, 15, n=16), wc) + L(ell(34, 60, 5, 5, n=10), closed=True, w=1.4) + S([(48, 56), (100, 56), (100, 64), (48, 64)], wc) + L([(82, 64), (82, 76), (90, 76), (90, 64)], w=1.5) + L([(94, 64), (94, 72), (100, 72)], w=1.5)
    elif kind == "lock":
        o = L([(44, 56), (44, 40), (50, 29), (60, 26), (70, 29), (76, 40), (76, 56)], w=2.2) + S(rect(34, 56, 52, 44), wc) + L(ell(60, 72, 5, 5, n=10), closed=True, w=1.4) + L([(60, 76), (60, 88)], w=2)
    elif kind == "unlock":
        o = L([(76, 56), (76, 40), (70, 29), (60, 26), (50, 29), (44, 40), (44, 46)], w=2.2) + S(rect(34, 56, 52, 44), wc) + L(ell(60, 72, 5, 5, n=10), closed=True, w=1.4) + L([(60, 76), (60, 88)], w=2)
    elif kind == "laptop":
        o = S(rect(28, 26, 64, 46), wc) + L(rect(34, 31, 52, 36), closed=True, w=1.1) + S([(16, 74), (104, 74), (108, 86), (12, 86)], wc) + L([(50, 80), (70, 80)], w=1.2)
    elif kind == "terminal":
        o = S(rect(14, 28, 92, 66), wc) + L([(14, 42), (106, 42)], w=1.2) + "".join(pen.dot(x, 35, 2) for x in (22, 30, 38)) + L([(24, 56), (32, 62), (24, 68)], w=1.6) + L([(38, 68), (54, 68)], w=1.6) + L([(24, 80), (70, 80)], w=1.1)
    elif kind == "server":
        o = S(rect(30, 18, 60, 84), wc) + L([(30, 46), (90, 46)], w=1.2) + L([(30, 74), (90, 74)], w=1.2) + "".join(pen.dot(38, y, 2) for y in (32, 60, 88)) + "".join(L([(50, y), (82, y)], w=1) for y in (30, 36, 58, 64, 86, 92))
    elif kind == "rack":
        o = S(rect(32, 8, 56, 104), wc) + "".join(L([(32, y), (88, y)], w=1.1) for y in range(24, 112, 16)) + "".join(pen.dot(40, y-8, 1.6) for y in range(24, 120, 16)) + "".join(L([(50, y-8), (80, y-8)], w=0.9) for y in range(24, 120, 16))
    elif kind == "cloud":
        c = [(24, 78), (16, 64), (26, 50), (44, 48), (52, 34), (72, 30), (86, 44), (100, 48), (106, 64), (98, 80), (84, 86), (36, 86)]
        o = S(c, wc)
    elif kind == "database":
        o = (pen.fill(rect(28, 36, 64, 54), wc, jitter=1) if pen.fills else "") + (pen.fill(ell(60, 90, 32, 10, n=16), wc, jitter=1) if pen.fills else "") + L([(28, 36), (28, 90)], w=1.5) + L([(92, 36), (92, 90)], w=1.5) + L(arc(60, 90, 32, 0, 180, n=12, ry=10), w=1.5) + L(arc(60, 62, 32, 0, 180, n=12, ry=10), w=1.2) + S(ell(60, 36, 32, 10, n=18), wc)
    elif kind == "phone":
        o = S(rect(40, 12, 40, 96), wc) + L(rect(44, 22, 32, 70), closed=True, w=1.1) + pen.dot(60, 100, 2.5)
    elif kind == "doc":
        o = S([(30, 12), (78, 12), (92, 26), (92, 108), (30, 108)], wc) + L([(78, 12), (78, 26), (92, 26)], w=1.3) + "".join(L([(40, y), (82, y)], w=1.1) for y in (44, 56, 68, 80)) + L([(40, 92), (64, 92)], w=1.1)
    elif kind == "folder":
        o = S([(14, 30), (46, 30), (54, 40), (106, 40), (106, 98), (14, 98)], wc) + L([(14, 46), (106, 46)], w=1.1)
    elif kind == "box":
        o = S(rect(28, 56, 64, 44), wc) + S([(28, 56), (12, 40), (46, 44), (60, 56)], wc) + S([(92, 56), (108, 40), (74, 44), (60, 56)], wc) + L([(46, 44), (60, 56), (74, 44)], w=1.2)
    elif kind == "cube":
        o = S([(30, 48), (74, 48), (74, 100), (30, 100)], wc) + S([(30, 48), (52, 28), (96, 28), (74, 48)], wc) + S([(74, 48), (96, 28), (96, 80), (74, 100)], wc, shade=[(74, 48), (96, 28), (96, 80), (74, 100)])
    elif kind == "router":
        o = S(rect(22, 66, 76, 26), wc) + L([(40, 66), (34, 30)], w=1.6) + L([(80, 66), (86, 30)], w=1.6) + "".join(pen.dot(x, 79, 2) for x in (36, 46, 56)) + L([(70, 79), (88, 79)], w=1.1)
    elif kind == "clock":
        o = S(ell(60, 62, 38, 38, n=24), wc) + L([(60, 62), (60, 36)], w=1.8) + L([(60, 62), (78, 70)], w=1.8) + "".join(L([(60+34*math.cos(a), 62+34*math.sin(a)), (60+30*math.cos(a), 62+30*math.sin(a))], w=1.2) for a in [math.radians(i*30) for i in range(12)])
    elif kind == "bulb":
        o = S(ell(60, 48, 24, 26, n=20), wc) + L([(48, 68), (46, 84), (74, 84), (72, 68)], w=1.4) + L([(48, 90), (72, 90)], w=1.5) + L([(52, 96), (68, 96)], w=1.5) + L([(56, 52), (60, 70), (64, 52)], w=1.1) + "".join(L([(60+34*math.cos(a), 48+34*math.sin(a)), (60+42*math.cos(a), 48+42*math.sin(a))], w=1.2) for a in [math.radians(x) for x in (200, 240, 300, 340)])
    elif kind == "bug":
        o = S(ell(60, 68, 22, 28, n=20), wc) + S(ell(60, 38, 12, 10, n=12), wc) + L([(60, 44), (60, 96)], w=1.2) + L([(52, 30), (44, 20)], w=1.3) + L([(68, 30), (76, 20)], w=1.3) + "".join(L([(38, y), (24, y-6)], w=1.4) + L([(82, y), (96, y-6)], w=1.4) for y in (56, 70, 84)) + "".join(pen.dot(x, y, 2.4) for x, y in ((50, 60), (70, 66), (56, 80), (68, 84)))
    elif kind == "shield":
        s_ = [(60, 14), (98, 28), (94, 68), (60, 106), (26, 68), (22, 28)]
        o = S(s_, wc) + L([(44, 60), (56, 72), (78, 46)], w=2.2)
    elif kind == "coin":
        o = S(ell(60, 62, 36, 36, n=24), wc) + L(ell(60, 62, 28, 28, n=20), closed=True, w=1.1) + f'<text x="60" y="72" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="28" font-weight="600" fill="currentColor">¢</text>'
    elif kind == "coffee":
        o = S([(30, 46), (84, 46), (78, 102), (36, 102)], wc) + L(arc(88, 66, 12, -80, 80, n=8, ry=14), w=1.6) + "".join(L([(x, 36), (x-3, 28), (x+2, 20), (x-2, 12)], w=1.2) for x in (46, 58, 70))
    elif kind == "globe":
        o = S(ell(60, 62, 38, 38, n=24), wc) + L(ell(60, 62, 16, 38, n=20), closed=True, w=1.1) + L([(22, 62), (98, 62)], w=1.1) + L(arc(60, 62, 36, 200, 340, n=10, ry=22), w=1.0) + L(arc(60, 62, 36, 20, 160, n=10, ry=22), w=1.0)
    elif kind == "gear":
        pts = []
        for i in range(16):
            a = math.radians(i*22.5); r = 40 if i % 2 == 0 else 30
            pts += [(60+r*math.cos(a-0.12), 62+r*math.sin(a-0.12)), (60+r*math.cos(a+0.12), 62+r*math.sin(a+0.12))]
        o = S(pts, wc) + L(ell(60, 62, 12, 12, n=12), closed=True, w=1.4)
    elif kind == "magnifier":
        o = S(ell(48, 50, 26, 26, n=20), wc) + L(ell(48, 50, 20, 20, n=16), closed=True, w=1.1) + L([(67, 69), (102, 104)], w=5) + L([(40, 40), (46, 34)], w=1.4)
    elif kind == "signpost":
        o = L([(60, 30), (60, 112)], w=2.4) + S([(24, 30), (84, 30), (94, 40), (84, 50), (24, 50)], wc) + S([(96, 60), (36, 60), (26, 70), (36, 80), (96, 80)], wc) + L([(34, 40), (74, 40)], w=1.1) + L([(46, 70), (86, 70)], w=1.1)
    elif kind == "plant":
        o = S([(38, 78), (82, 78), (76, 110), (44, 110)], "var(--w-clay)") + L([(60, 78), (60, 44)], w=1.6) + S(ell(46, 48, 12, 6, n=12, rot=-0.7), "var(--w-sage)") + S(ell(74, 40, 12, 6, n=12, rot=0.6), "var(--w-sage)") + S(ell(58, 28, 6, 11, n=12), "var(--w-sage)")
    elif kind == "flag":
        o = L([(30, 14), (30, 112)], w=2.2) + S([(30, 18), (56, 26), (80, 16), (100, 26), (100, 64), (80, 54), (56, 64), (30, 56)], wc)
    elif kind == "chain":
        o = S(ell(42, 62, 22, 12, n=16, rot=-0.6, sq=2.6), wc) + S(ell(78, 62, 22, 12, n=16, rot=-0.6, sq=2.6), wc)
    elif kind == "fire":
        f_ = [(60, 14), (76, 40), (72, 58), (86, 68), (80, 96), (60, 108), (40, 96), (34, 68), (48, 58), (44, 40)]
        o = S(f_, "var(--w-clay)") + S([(60, 62), (70, 78), (66, 96), (54, 96), (50, 78)], "var(--w-ochre)")
    elif kind == "trash":
        o = S([(34, 40), (86, 40), (80, 108), (40, 108)], wc) + L([(26, 40), (94, 40)], w=1.8) + L([(50, 40), (52, 30), (68, 30), (70, 40)], w=1.4) + "".join(L([(x, 52), (x, 96)], w=1.1) for x in (50, 60, 70))
    elif kind == "git":
        o = L([(40, 100), (40, 30)], w=1.6) + L([(40, 70), (60, 56), (80, 40)], w=1.6) + "".join(S(ell(x, y, 7, 7, n=10), wc) for x, y in ((40, 100), (40, 70), (40, 30), (80, 40)))
    elif kind == "dice":
        o = S(ell(60, 62, 34, 34, n=20, sq=4), wc) + "".join(pen.dot(x, y, 4) for x, y in ((44, 46), (76, 46), (60, 62), (44, 78), (76, 78)))
    elif kind == "hash":
        o = L([(44, 24), (36, 100)], w=2.2) + L([(76, 24), (68, 100)], w=2.2) + L([(26, 50), (98, 50)], w=2.2) + L([(22, 76), (94, 76)], w=2.2)
    elif kind == "fingerprint":
        o = "".join(L(arc(60, 66, r, 200, 340+min(r, 40)/2, n=14, ry=r*1.15), w=1.2) for r in (8, 15, 22, 29, 36)) + L(arc(60, 66, 36, 120, 190, n=6, ry=41), w=1.2) + L(arc(60, 66, 29, 130, 185, n=6, ry=33), w=1.2)
    elif kind == "book":
        o = S([(18, 30), (56, 36), (56, 104), (18, 98)], wc) + S([(102, 30), (64, 36), (64, 104), (102, 98)], wc) + L([(56, 36), (60, 40), (64, 36)], w=1.4) + L([(60, 40), (60, 108)], w=1.4) + "".join(L([(26, y), (50, y+2)], w=0.9) for y in (48, 58, 68)) + "".join(L([(70, y+2), (94, y)], w=0.9) for y in (48, 58, 68))
    elif kind == "pencil":
        o = S([(26, 84), (76, 34), (88, 46), (38, 96)], "var(--w-ochre)") + L([(40, 70), (52, 82)], w=1.1) + S([(76, 34), (86, 24), (98, 36), (88, 46)], "var(--w-clay)") + L([(26, 84), (18, 104), (38, 96)], w=1.4) + pen.fill([(18, 104), (22, 96), (26, 100)], "currentColor", dx=0, dy=0)
    elif kind == "stamp":
        o = S(rect(28, 82, 64, 16), wc) + L([(50, 82), (52, 62), (68, 62), (70, 82)], w=1.5) + S(ell(60, 52, 14, 10, n=14), wc) + L([(34, 108), (86, 108)], w=1.6)
    elif kind == "bell":
        o = S([(38, 84), (40, 56), (48, 36), (60, 30), (72, 36), (80, 56), (82, 84), (92, 92), (28, 92)], wc) + L([(60, 30), (60, 22)], w=1.6) + pen.dot(60, 20, 3) + L(arc(60, 96, 8, 0, 180, n=8, ry=8), w=1.6)
    elif kind == "hourglass":
        o = L([(34, 20), (86, 20)], w=2) + L([(34, 108), (86, 108)], w=2) + S([(38, 22), (82, 22), (64, 62), (82, 106), (38, 106), (56, 62)], wc) + pen.fill([(44, 28), (76, 28), (62, 56), (58, 56)], "var(--w-ochre)", dx=0, dy=0) + pen.fill([(46, 100), (74, 100), (62, 88), (58, 88)], "var(--w-ochre)", dx=0, dy=0)
    elif kind == "battery":
        o = S(rect(20, 42, 76, 40), wc) + L([(96, 52), (104, 52), (104, 72), (96, 72)], w=1.6) + "".join(pen.fill(rect(x, 50, 12, 24), "currentColor", dx=0, dy=0, jitter=0.4) for x in (28, 46))
    elif kind == "wifi":
        o = "".join(L(arc(60, 92, r, 215, 325, n=10), w=2) for r in (18, 34, 50)) + pen.dot(60, 92, 4)
    elif kind == "dish":
        o = S(arc(60, 50, 40, 20, 200, n=14, ry=26) + [(60, 50)], wc) + L([(60, 62), (60, 108)], w=2.2) + L([(40, 108), (80, 108)], w=2) + L([(60, 50), (84, 22)], w=1.4) + pen.dot(86, 20, 3.5)
    elif kind == "hammer":
        o = S([(30, 30), (74, 30), (82, 42), (74, 54), (30, 54)], wc) + L([(58, 54), (48, 110)], w=5) + L([(84, 42), (94, 36)], w=1.4)
    elif kind == "wrench":
        o = S([(22, 96), (56, 62), (50, 46), (62, 30), (78, 38), (70, 50), (66, 60), (34, 106)], wc) + L(ell(64, 42, 5, 5, n=8), closed=True, w=1.3)
    elif kind == "pin":
        o = S([(60, 112), (36, 74), (28, 50), (40, 26), (60, 18), (80, 26), (92, 50), (84, 74)], "var(--w-clay)") + L(ell(60, 48, 12, 12, n=12), closed=True, w=1.4)
    elif kind == "calendar":
        o = S(rect(20, 30, 80, 76), wc) + L([(20, 48), (100, 48)], w=1.4) + L([(38, 22), (38, 38)], w=2) + L([(82, 22), (82, 38)], w=2) + "".join(pen.dot(x, y, 2.2) for x in (36, 52, 68, 84) for y in (62, 78, 92))
    elif kind == "chart":
        o = L([(22, 20), (22, 100), (104, 100)], w=1.8) + S(rect(32, 70, 12, 30), wc) + S(rect(50, 52, 12, 48), wc) + S(rect(68, 62, 12, 38), wc) + S(rect(86, 30, 12, 70), wc)
    elif kind == "tag":
        o = S([(18, 38), (62, 38), (104, 80), (62, 112), (18, 112)], wc) + L(ell(34, 56, 5, 5, n=8), closed=True, w=1.3)
    elif kind == "check":
        o = L([(24, 64), (50, 92), (100, 30)], w=4, color=GREEN)
    elif kind == "cross":
        o = L([(30, 30), (92, 96)], w=4, color=RED) + L([(92, 30), (30, 96)], w=4, color=RED)
    elif kind == "question":
        o = L([(40, 44), (44, 26), (60, 20), (76, 28), (76, 46), (62, 58), (60, 72)], w=3.4, color=PENC) + pen.dot(60, 92, 4.4, PENC)
    elif kind == "vm":
        o = S(rect(18, 26, 84, 68), wc) + L(rect(28, 36, 30, 22), closed=True, w=1.2) + L(rect(64, 36, 30, 22), closed=True, w=1.2) + L(rect(28, 64, 66, 20), closed=True, w=1.2) + L([(18, 94), (12, 104), (108, 104), (102, 94)], w=1.4)
    elif kind == "sandbox":
        o = S(rect(22, 60, 76, 40), wc) + L([(22, 60), (10, 46), (40, 50), (52, 60)], w=1.4) + L([(98, 60), (110, 46), (80, 50), (68, 60)], w=1.4) + "".join(pen.dot(x, y, 1.3) for x, y in ((40, 74), (62, 70), (80, 78), (50, 88), (72, 90), (34, 92)))
    elif kind == "process":
        o = S(ell(60, 62, 24, 24, n=18), wc) + L([(48, 54), (72, 54)], w=1.4) + L([(48, 62), (66, 62)], w=1.4) + L([(48, 70), (70, 70)], w=1.4) + L(arc(60, 62, 30, -60, 30, n=8), w=1.3) + L([(86, 46), (88, 38), (80, 42)], w=1.3)
    elif kind == "rocket":
        o = S([(60, 14), (76, 40), (78, 80), (42, 80), (44, 40)], wc) + L(ell(60, 46, 7, 7, n=10), closed=True, w=1.3) + S([(42, 66), (26, 90), (44, 84)], "var(--w-clay)") + S([(78, 66), (94, 90), (76, 84)], "var(--w-clay)") + S([(50, 84), (70, 84), (60, 108)], "var(--w-ochre)")
    elif kind == "heart":
        o = S([(60, 104), (24, 66), (20, 40), (36, 26), (60, 38), (84, 26), (100, 40), (96, 66)], "var(--w-clay)")
    elif kind == "star":
        pts = [(60+(40 if i % 2 == 0 else 17)*math.cos(math.radians(-90+i*36)), 64+(40 if i % 2 == 0 else 17)*math.sin(math.radians(-90+i*36))) for i in range(10)]
        o = S(pts, "var(--w-ochre)")
    elif kind == "eye":
        o = S([(16, 62), (36, 40), (60, 32), (84, 40), (104, 62), (84, 84), (60, 92), (36, 84)], wc) + L(ell(60, 62, 14, 14, n=14), closed=True, w=1.5) + pen.dot(60, 62, 6)
    elif kind == "ear":
        o = L(arc(60, 60, 26, 100, 380, n=14, ry=34), w=1.8) + L(arc(60, 66, 14, 80, 300, n=10, ry=20), w=1.3) + L([(60, 92), (56, 104), (48, 108)], w=1.6)
    elif kind == "handwave":
        o = S([(40, 110), (36, 60), (44, 56), (46, 76), (48, 40), (56, 40), (58, 72), (60, 30), (68, 30), (70, 72), (74, 36), (82, 38), (80, 76), (90, 62), (96, 68), (84, 106)], "var(--w-clay)")
    elif kind == "mail-open":
        o = L([(18, 50), (60, 20), (102, 50)], w=1.5) + S(rect(28, 36, 64, 40), "var(--w-gray)") + S([(18, 50), (60, 80), (102, 50), (102, 100), (18, 100)], wc)
    elif kind == "keyboard":
        o = S(rect(12, 40, 96, 48), wc) + "".join(L(rect(x, y, 8, 7), closed=True, w=0.9) for y in (46, 57) for x in range(18, 100, 12)) + L(rect(30, 70, 60, 8), closed=True, w=1)
    elif kind == "cpu":
        o = S(rect(30, 30, 60, 60), wc) + L(rect(44, 44, 32, 32), closed=True, w=1.2) + "".join(L([(x, 30), (x, 18)], w=1.3) + L([(x, 90), (x, 102)], w=1.3) for x in (42, 54, 66, 78)) + "".join(L([(30, y), (18, y)], w=1.3) + L([(90, y), (102, y)], w=1.3) for y in (42, 54, 66, 78))
    elif kind == "clipboard":
        o = S(rect(28, 26, 64, 84), wc) + S(rect(46, 18, 28, 14), "var(--w-gray)") + "".join(L([(40, y), (56, y+12)], w=1.6, color=GREEN) + L([(56, y+12), (64, y-4)], w=1.6, color=GREEN) + L([(70, y+4), (84, y+4)], w=1) for y in (48, 70))
    return o

def face_on(pen, kind, mood="neutral", wash="blue"):
    """object with a face"""
    o = obj(pen, kind, wash)
    moods = {
        "neutral": ("dot", "flat", "flat"), "happy": ("dot", "flat", "smile"), "grumpy": ("oval", "angry", "frown"), "sleepy": ("sleepy", "none", "flat"),
        "shock": ("wide", "raised", "o"), "smug": ("hooded", "one-up", "smirk"), "angry": ("oval", "angry", "grit"), "sad": ("dot", "worried", "frown"), "wink": ("wink", "flat", "smile"),
    }
    e, b, m = moods.get(mood, moods["neutral"])
    pos = {"server": (60, 60, 0.55), "box": (60, 78, 0.5), "sandbox": (60, 80, 0.5), "cloud": (62, 62, 0.55), "bug": (60, 66, 0.5), "key": (34, 60, 0.32), "lock": (60, 78, 0.5), "laptop": (60, 50, 0.5), "database": (60, 62, 0.6), "envelope": (60, 66, 0.5), "coin": (60, 62, 0.6), "bulb": (60, 48, 0.5), "phone": (60, 58, 0.55), "cube": (52, 74, 0.5), "coffee": (58, 74, 0.55), "vm": (60, 60, 0.5), "process": (60, 62, 0.55), "doc": (60, 62, 0.5), "rocket": (60, 60, 0.4), "globe": (60, 62, 0.6), "clock": (60, 62, 0.5), "terminal": (60, 66, 0.5), "trash": (60, 74, 0.5), "gear": (60, 62, 0.5)}
    cx, cy, s = pos.get(kind, (60, 62, 0.5))
    inner = brows(pen, b) + eyes(pen, e) + mouth(pen, m) + (pen.dot(46, 74, 4, "#d59a9a").replace("></circle>", ' opacity=".35"></circle>') + pen.dot(76, 74, 4, "#d59a9a").replace("></circle>", ' opacity=".35"></circle>') if mood in ("happy", "wink") else "")
    return o + f'<g transform="translate({cx-60*s} {cy-62*s}) scale({s})">{inner}</g>'

# ---------------- connectors and annotations (in any coordinate space) ----------------
def arrow(pen, p0, p1, curve=0.0, dashed=False, head=True, w=1.8, color="currentColor", both=False, tail_len=11):
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0+x1)/2, (y0+y1)/2
    dx, dy = x1-x0, y1-y0; L = math.hypot(dx, dy) or 1
    nx, ny = -dy/L, dx/L
    ctrl = (mx+nx*curve*2, my+ny*curve*2)
    if curve:
        pts = [((1-t)**2*x0 + 2*(1-t)*t*ctrl[0] + t**2*x1, (1-t)**2*y0 + 2*(1-t)*t*ctrl[1] + t**2*y1) for t in [i/14 for i in range(15)]]
    else:
        pts = [p0, p1]
    d = pen.line(pts, w=w, color=color, step=8)
    if dashed:
        d = d.replace('stroke-linejoin="round"', 'stroke-linejoin="round" stroke-dasharray="7 6"')
    def hd(tip, frm):
        ax, ay = tip[0]-frm[0], tip[1]-frm[1]; l = math.hypot(ax, ay) or 1; ax, ay = ax/l, ay/l
        px, py = -ay, ax
        a = (tip[0]-ax*tail_len+px*tail_len*0.6, tip[1]-ay*tail_len+py*tail_len*0.6)
        b = (tip[0]-ax*tail_len-px*tail_len*0.6, tip[1]-ay*tail_len-py*tail_len*0.6)
        return pen.line([a, tip, b], w=w, color=color, jitter=0.4, step=8, dbl=False)
    if head: d += hd(p1, pts[-2] if curve else p0)
    if both: d += hd(p0, pts[1] if curve else p1)
    return d

def lightning(pen, p0, p1, color=RED, w=2.2):
    (x0, y0), (x1, y1) = p0, p1
    pts = [p0, (x0+(x1-x0)*0.4+(y1-y0)*0.12, y0+(y1-y0)*0.4-(x1-x0)*0.12), (x0+(x1-x0)*0.55-(y1-y0)*0.12, y0+(y1-y0)*0.55+(x1-x0)*0.12), p1]
    return pen.line(pts, w=w, color=color, jitter=0.3, step=40, dbl=False)

def bubble(pen, x, y, w, h, tail="bl", kind="round", fill=PAPER, color="currentColor", to=None, gap=6):
    """A speech bubble with a short wedge aimed at the speaker.
    Directed tails share one closed outline with the body so jitter cannot open a seam.
    Otherwise `tail` selects the legacy fixed-corner wedge."""
    cx, cy, rx, ry = x + w/2, y + h/2, w/2, h/2
    if kind == "spiky":
        pts = []
        n = 18
        for i in range(n):
            a = 2*math.pi*i/n; r = 1.0 if i % 2 == 0 else 0.78
            pts.append((cx + rx*r*math.cos(a), cy + ry*r*math.sin(a)))
        return pen.fill(pts, fill, dx=0, dy=0, jitter=0.6) + pen.line(pts, closed=True, w=1.6, color=color, jitter=0.3, step=30)
    if kind == "thought":
        pts = ell(cx, cy, rx, ry, n=16)
        body = pen.fill(pts, fill, dx=0, dy=0, jitter=3) + pen.line(pts, closed=True, w=1.5, color=color, jitter=3.2, step=9)
        if to is not None:
            dx, dy = to[0] - cx, to[1] - cy; L = math.hypot(dx, dy) or 1
            t = math.atan2(dy/ry, dx/rx)
            ex, ey = cx + rx*math.cos(t), cy + ry*math.sin(t)
            for k, r in ((0.35, 6), (0.7, 3.5)):
                px, py = ex + (to[0]-gap*dx/L - ex)*k, ey + (to[1]-gap*dy/L - ey)*k
                body += pen.line(ell(px, py, r, r*0.85, n=8), closed=True, w=1.3, color=color)
        elif tail == "bl":
            body += pen.line(ell(x+w*0.2, y+h+10, 6, 5, n=8), closed=True, w=1.3, color=color) + pen.line(ell(x+w*0.12, y+h+24, 3.5, 3, n=8), closed=True, w=1.2, color=color)
        elif tail == "br":
            body += pen.line(ell(x+w*0.8, y+h+10, 6, 5, n=8), closed=True, w=1.3, color=color) + pen.line(ell(x+w*0.88, y+h+24, 3.5, 3, n=8), closed=True, w=1.2, color=color)
        return body
    pts = rect(x, y, w, h) if kind == "rect" else ell(cx, cy, rx, ry, n=20, sq=3.2)
    if to is not None:
        # where the ray centre→chin leaves the body: intersect it with the polygon actually drawn (a squircle, not an ellipse)
        dx, dy = to[0] - cx, to[1] - cy
        best = None
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i+1) % len(pts)]
            sx, sy = x2 - x1, y2 - y1
            den = dx*sy - dy*sx
            if abs(den) < 1e-9: continue
            tr = ((x1-cx)*sy - (y1-cy)*sx) / den
            ts = ((x1-cx)*dy - (y1-cy)*dx) / den
            if tr > 0 and 0 <= ts <= 1 and (best is None or tr < best): best = tr
        best = best if best is not None else 1.0
        ex, ey = cx + dx*best, cy + dy*best
        vx, vy = to[0] - ex, to[1] - ey
        L = math.hypot(vx, vy) or 1
        ux, uy = vx/L, vy/L
        px, py = -uy, ux
        length = max(10, min(22, L - gap))
        tip = (ex + ux*length - px*7, ey + uy*length - py*7)
        # Remove a short arc from the body and route that same contour through
        # the tip. Filling/stroking one path avoids both a gap and an inner seam.
        perimeter = resample(pts, pen._step(6), True)
        n = len(perimeter)
        centre = min(range(n), key=lambda i: math.hypot(perimeter[i][0]-ex, perimeter[i][1]-ey))
        ends = []
        for direction in (-1, 1):
            i, distance = centre, 0
            while distance < min(15, w/4, h/4):
                j = (i + direction) % n
                distance += math.dist(perimeter[i], perimeter[j])
                i = j
            ends.append(i)
        before, after = ends
        contour = [tip]
        i = after
        while True:
            contour.append(perimeter[i])
            if i == before: break
            i = (i + 1) % n
        outline = pen.line(contour, closed=True, w=1.5, color=color, dbl=False)
        return outline.replace('fill="none"', f'fill="{fill}"', 1)
    else:
        body = pen.fill(pts, fill, dx=0, dy=0, jitter=0.8) + pen.line(pts, closed=True, w=1.5, color=color)
        tails = {
            "bl": [(x+w*0.25, y+h-2), (x+w*0.16, y+h+18), (x+w*0.4, y+h-2)],
            "br": [(x+w*0.75, y+h-2), (x+w*0.84, y+h+18), (x+w*0.6, y+h-2)],
            "l": [(x+2, y+h*0.5), (x-18, y+h*0.62), (x+2, y+h*0.72)],
            "r": [(x+w-2, y+h*0.5), (x+w+18, y+h*0.62), (x+w-2, y+h*0.72)],
            "tl": [(x+w*0.25, y+2), (x+w*0.16, y-18), (x+w*0.4, y+2)],
            "none": None,
        }
        tp = tails.get(tail)
    if tp:
        body += pen.fill(tp, fill, dx=0, dy=0, jitter=0.3) + pen.line(tp, w=1.5, color=color, jitter=0.4, step=30, dbl=False)
    return body

def text(x, y, s, size=13, font="mono", color="currentColor", anchor="start", weight=400, rot=0):
    ff = "'IBM Plex Mono', monospace" if font == "mono" else "Caveat, cursive"
    r = f' transform="rotate({rot} {x} {y})"' if rot else ""
    return f'<text x="{x}" y="{y}" font-family="{ff}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{r}>{s}</text>'

def stamp(pen, x, y, label, color=RED, rot=-8, w=None, size=15):
    w = w or (len(label)*size*0.66 + 28)
    h = size*2.1
    pts = rect(x, y, w, h)
    s = pen.line(pts, closed=True, w=2.2, color=color, jitter=0.7) + pen.line(rect(x+4, y+4, w-8, h-8), closed=True, w=1, color=color, jitter=0.5)
    s += text(x+w/2, y+h*0.68, label, size=size, color=color, anchor="middle", weight=600)
    return f'<g transform="rotate({rot} {x+w/2} {y+h/2})" opacity=".9">{s}</g>'

def pin_num(pen, x, y, n, color=PENC, r=11):
    return pen.fill(ell(x, y, r, r, n=12), PAPER, dx=0, dy=0, jitter=0.4) + pen.line(ell(x, y, r, r, n=12), closed=True, w=1.6, color=color) + text(x, y+4.5, str(n), size=13, color=color, anchor="middle", weight=600)

def tape(pen, x, y, w=70, rot=-6, color="var(--w-ochre)"):
    pts = [(x, y), (x+w, y+1), (x+w-3, y+9), (x+w, y+17), (x, y+18), (x+3, y+9)]
    return f'<g transform="rotate({rot} {x+w/2} {y+9})" opacity=".85">{pen.fill(pts, color, dx=0, dy=0, jitter=0.5)}</g>'

def circle_emph(pen, cx, cy, rx, ry, color=PENC):
    pts = ell(cx, cy, rx, ry, n=22)
    return pen.line(pts + pts[:4], w=1.8, color=color, jitter=1.6, step=8, dbl=False)

def crossout(pen, x0, y0, x1, y1, color=RED):
    return pen.line([(x0, y0), (x1, y1)], w=2, color=color) + pen.line([(x0, y1), (x1, y0)], w=2, color=color)

def underline_scribble(pen, x, y, w, color=PENC):
    n = max(3, int(w/22))
    pts = [(x + w*i/n, y + (2 if i % 2 else -2)) for i in range(n+1)]
    return pen.line(pts, w=2, color=color, jitter=0.8, step=8, dbl=False)

def bracket(pen, x, y0, y1, side="l", color="currentColor"):
    d = -8 if side == "l" else 8
    return pen.line([(x, y0), (x+d, y0+4), (x+d, (y0+y1)/2-4), (x+d*2, (y0+y1)/2), (x+d, (y0+y1)/2+4), (x+d, y1-4), (x, y1)], w=1.6, color=color, step=8)

def sparkles(pen, x, y, color=PENC):
    o = ""
    for (dx, dy, s) in [(0, 0, 6), (16, -10, 4), (-14, 12, 3.5)]:
        o += pen.line([(x+dx-s, y+dy), (x+dx+s, y+dy)], w=1.4, color=color, dbl=False) + pen.line([(x+dx, y+dy-s), (x+dx, y+dy+s)], w=1.4, color=color, dbl=False)
    return o

def paperclip(pen, x, y, rot=15):
    pts = [(x+4, y+30), (x+4, y+6), (x+8, y+2), (x+12, y+6), (x+12, y+36), (x+8, y+40), (x+0, y+40), (x-4, y+36), (x-4, y+12), (x+0, y+8), (x+4, y+12), (x+4, y+30)]
    return f'<g transform="rotate({rot} {x+4} {y+20})">{pen.line(pts, w=1.6, jitter=0.4, step=6, dbl=False)}</g>'

def tack(pen, x, y, color=RED):
    return pen.fill(ell(x, y, 6, 6, n=10), color, dx=0, dy=0, jitter=0.3) + pen.line(ell(x, y, 6, 6, n=10), closed=True, w=1.2) + pen.line([(x, y+6), (x+2, y+18)], w=1.4)
