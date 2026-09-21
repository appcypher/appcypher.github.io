#!/usr/bin/env python3
"""Cover doodle for the "Mario never dies" post: a player standing on the frozen copy,
four futures fanning out of it, three collapsed, one carrying on.

Writes _includes/doodles/covers/mario-never-dies.svg. Run from the repo root:
python3 tools/gen_cover_mario.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import doodle as D
from doodle import Pen

W = D.WASH
LINE_Y, NODE_X = 60, 44
FUTURES = [(98, 20, .34), (98, 45, .14), (98, 76, -.16), (98, 104, -.36)]
SURVIVOR = 2


def player(pen, cap="clay", skin="ochre"):
    """A generic platform-game character, 26 wide and 30 tall, feet at y=30."""
    S, L, dot = pen.shape, pen.line, pen.dot
    s  = S(D.rect(5, -5, 16, 6), W[cap])                      # cap
    s += S(D.rect(3, 0, 20, 5), W[cap])                       # brim
    s += S(D.rect(5, 5, 16, 11), W[skin])                     # head
    s += dot(10, 10, 1.7) + dot(17, 10, 1.7)                  # eyes
    s += S(D.rect(3, 16, 20, 9), W[cap])                      # body
    s += L([(3, 20), (-2, 21)], w=1.5) + L([(23, 20), (28, 21)], w=1.5)
    s += L([(8, 25), (8, 30)], w=1.8) + L([(18, 25), (18, 30)], w=1.8)
    return s


def cover():
    # the backing: loose blue hatching, kept quiet so the lines stay on top
    bg = Pen(seed=13, style=3, rough=1.0).hatch(
        D.ell(60, 62, 58, 58), spacing=11, angle=60, color=W["blue"], w=1.3, op=.75)

    p = Pen(seed=24, style=3, rough=.9)
    L, S = p.line, p.shape
    s  = L([(2, LINE_Y), (NODE_X, LINE_Y)], w=2.8)            # the past
    s += D.place(player(Pen(seed=64, style=3, rough=.9)), 6, LINE_Y - 31.5, 1.05)
    s += S(D.ell(NODE_X, LINE_Y, 5.5, 5.5, n=14), W["blue"])  # the frozen copy
    s += L(D.ell(NODE_X, LINE_Y, 5.5, 5.5, n=14), closed=True, w=1.6)

    for i, (ex, ey, curve) in enumerate(FUTURES):
        survivor = (i == SURVIVOR)
        s += D.arrow(p, (50, LINE_Y), (ex - 6, ey), curve=curve, head=False,
                     w=2.6 if survivor else 1.4,
                     color=D.PENC if survivor else "currentColor")
        if not survivor:
            s += D.crossout(p, ex - 6, ey - 7, ex + 6, ey + 5)
    s += D.arrow(p, (92, 76), (116, 84), curve=.1, w=2.6, color=D.PENC)

    return f'<svg viewBox="0 0 120 120" aria-hidden="true" focusable="false">{bg}{s}</svg>\n'


out = os.path.join(ROOT, "_includes", "doodles", "covers")
os.makedirs(out, exist_ok=True)
path = os.path.join(out, "mario-never-dies.svg")
open(path, "w").write(cover())
print("wrote", os.path.relpath(path, ROOT))
