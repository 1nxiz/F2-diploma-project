"""Render the use case diagram as UML-notation SVG (preview for documents)."""
import math, sys, textwrap
from uc_model import *

W, H = 1400, 1000
out = []
def add(s): out.append(s)

def wrap(label, width=26):
    return textwrap.wrap(label, width) or [label]

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">')
add('<defs><marker id="open" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" fill="none" stroke="#222" stroke-width="1.4"/></marker>'
    '<marker id="tri" viewBox="0 0 12 12" refX="12" refY="6" markerWidth="14" markerHeight="14" orient="auto-start-reverse"><path d="M0,0 L12,6 L0,12 Z" fill="#fff" stroke="#222" stroke-width="1.2"/></marker></defs>')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')
s = SUBJECT
add(f'<rect x="{s["x0"]}" y="{s["y0"]}" width="{s["x1"]-s["x0"]}" height="{s["y1"]-s["y0"]}" fill="#fbfbfd" stroke="#333" stroke-width="1.5"/>')
add(f'<text x="{(s["x0"]+s["x1"])/2}" y="{s["y0"]+24}" text-anchor="middle" font-size="17" font-weight="bold">{s["name"]}</text>')

def ell_edge(cx, cy, tx, ty, a=UC_W/2, b=UC_H/2):
    dx, dy = tx-cx, ty-cy
    if dx == 0 and dy == 0: return cx, cy
    t = 1/math.sqrt((dx*dx)/(a*a)+(dy*dy)/(b*b))
    return cx+dx*t, cy+dy*t

def actor_edge(cx, cy, tx, ty):
    return (cx + (24 if tx > cx else -24), cy)

def pos(k):
    if k in ACTORS: return ACTORS[k][1], ACTORS[k][2]
    return USE_CASES[k][1], USE_CASES[k][2]

def edge_pts(a, b):
    ax, ay = pos(a); bx, by = pos(b)
    p1 = actor_edge(ax, ay, bx, by) if a in ACTORS else ell_edge(ax, ay, bx, by)
    p2 = actor_edge(bx, by, ax, ay) if b in ACTORS else ell_edge(bx, by, ax, ay)
    return p1, p2

def assoc_pts(a, b):
    ax, ay = pos(a); bx, by = pos(b)
    side = -1 if ax < bx else 1
    return actor_edge(ax, ay, bx, by), (bx + side*UC_W/2, by)
for a, b in ASSOCIATIONS:
    (x1, y1), (x2, y2) = assoc_pts(a, b)
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#222" stroke-width="1.3"/>')
for c, p in GENERALIZATIONS:
    cx, cy = pos(c); px, py = pos(p)
    add(f'<line x1="{cx}" y1="{cy-46}" x2="{px}" y2="{py+50}" stroke="#222" stroke-width="1.3" marker-end="url(#tri)"/>')
placed = []
def dashed(a, b, label):
    wp = WAYPOINTS.get((a, b))
    if wp:
        ax, ay = pos(a); bx, by = pos(b)
        pts = [ell_edge(ax, ay, *wp[0])] + wp + [ell_edge(bx, by, *wp[-1])]
        add('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '" fill="none" stroke="#222" stroke-width="1.2" stroke-dasharray="7,5" marker-end="url(#open)"/>')
        (x1, y1), (x2, y2) = pts[0], pts[1]
    else:
        (x1, y1), (x2, y2) = edge_pts(a, b)
        add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#222" stroke-width="1.2" stroke-dasharray="7,5" marker-end="url(#open)"/>')
    for t in (0.5, 0.3, 0.7, 0.2, 0.8):
        mx, my = x1+(x2-x1)*t, y1+(y2-y1)*t
        if all(abs(mx-px) > 70 or abs(my-py) > 22 for px, py in placed): break
    placed.append((mx, my))
    add(f'<text x="{mx:.1f}" y="{my-5:.1f}" text-anchor="middle" font-size="12" fill="#333" style="paint-order:stroke" stroke="#fff" stroke-width="4">{label}</text>')
for b, i in INCLUDES: dashed(b, i, "«include»")
for e, b in EXTENDS: dashed(e, b, "«extend»")

for k, (label, cx, cy) in USE_CASES.items():
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{UC_W/2}" ry="{UC_H/2}" fill="#fff8dc" stroke="#7a5c00" stroke-width="1.4"/>')
    lines = wrap(label)
    for j, ln in enumerate(lines):
        y = cy + (j - (len(lines)-1)/2)*15 + 5
        add(f'<text x="{cx}" y="{y:.1f}" text-anchor="middle" font-size="13">{ln}</text>')

for k, (label, cx, cy) in ACTORS.items():
    top = cy - 40
    add(f'<g stroke="#222" stroke-width="1.6" fill="none"><circle cx="{cx}" cy="{top+9}" r="9" fill="#fff"/>'
        f'<line x1="{cx}" y1="{top+18}" x2="{cx}" y2="{top+48}"/><line x1="{cx-16}" y1="{top+28}" x2="{cx+16}" y2="{top+28}"/>'
        f'<line x1="{cx}" y1="{top+48}" x2="{cx-13}" y2="{top+70}"/><line x1="{cx}" y1="{top+48}" x2="{cx+13}" y2="{top+70}"/></g>')
    add(f'<text x="{cx}" y="{top+88}" text-anchor="middle" font-size="13" font-weight="bold">{label}</text>')
add('</svg>')
open(sys.argv[1], "w").write("\n".join(out))
