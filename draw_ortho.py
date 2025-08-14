from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from nfa_core import Frag

# ===== Escala de grilla =====
DX = 2.0
DY = 1.8

# ===== Estilo =====
ARROW_SIZE = 8     
EPS_COLOR  = "#6b6b6b"   # gris para epsilon
SYM_COLOR  = "#000000"   # negro para símbolos
EPS_LW     = 1.4
SYM_LW     = 1.9

ARC_UP_SIGN = -1 
ARROW_SIZE = 5         
SHRINK_PT  = 16         
ARROW_STYLE = "Simple,head_length=3,head_width=3,tail_width=1.0"


def _pt(c: int, r: int) -> Tuple[float, float]:
    return c * DX, -r * DY

def _mid(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    return (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0

def _label(ax, x, y, s, color, z):
    ax.text(x, y, s, ha="center", va="bottom", fontsize=10, color=color,
            bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"), zorder=z)

def _arc_arrow(ax, p1, p2, *, up: bool, rad: float, color: str, lw: float, z: int):
    if p1 == p2:
        return
    sign = ARC_UP_SIGN if up else -ARC_UP_SIGN
    cs = f"arc3,rad={sign*abs(rad)}"
    patch = FancyArrowPatch(
        p1, p2,
        connectionstyle=cs,
        arrowstyle=ARROW_STYLE,          
        mutation_scale=ARROW_SIZE,
        lw=lw, color=color, zorder=z,
        clip_on=False,
        shrinkA=SHRINK_PT, shrinkB=SHRINK_PT  
    )
    ax.add_patch(patch)

def _line_arrow(ax, p1, p2, color: str, lw: float, z: int):
    patch = FancyArrowPatch(
        p1, p2,
        arrowstyle=ARROW_STYLE,         
        mutation_scale=ARROW_SIZE,
        lw=lw, color=color, zorder=z,
        clip_on=False,
        shrinkA=SHRINK_PT, shrinkB=SHRINK_PT  
    )
    ax.add_patch(patch)


def draw_fragment_ortho(frag: Frag, filename: str) -> None:
    out = Path(filename).with_suffix(".png")
    out.parent.mkdir(parents=True, exist_ok=True)

    # límites de figura
    xs, ys = [], []
    for (c, r) in frag.pos.values():
        x, y = _pt(c, r); xs.append(x); ys.append(y)
    margin = 1.8
    fig_w = max(7.0, (max(xs) - min(xs)) + 4.2)
    fig_h = max(4.6, (max(ys) - min(ys)) + 4.2)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(min(xs) - margin, max(xs) + margin)
    ax.set_ylim(min(ys) - margin, max(ys) + margin)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

    # flecha de inicio
    sx, sy = _pt(*frag.pos[frag.start])
    _line_arrow(ax, (sx - DX * 0.9, sy), (sx - 0.05, sy), color=SYM_COLOR, lw=SYM_LW, z=10)

    # carriles por fila
    lanes = {
        'roof': defaultdict(int),   # ε bypass largo (mismo r, span>=2)
        'up': defaultdict(int),     # loops hacia atrás
        'down': defaultdict(int),   # símbolo con ε-compañero (rombo bajo)
    }

    # curvaturas base y separación entre carriles
    base = {
        'roof': 0.30,   # techos (ε largos)
        'up':   0.22,   # loops ε hacia atrás
        'down': 0.20,   # triángulo inferior para símbolo
    }
    step = 0.10        # extra por carril
    span_boost = 0.03  # más separación horizontal -> más curvo
    gap = 0.06         # holgura entre roof y up en la misma fila

    roof_used = defaultdict(list)  # fila-> [rad usados]
    up_used   = defaultdict(list)

    # utilidades
    def same_row(s, t): return frag.pos[s][1] == frag.pos[t][1]
    def span(s, t):     return frag.pos[t][0] - frag.pos[s][0]

    # ε-compañeros: ¿existe ε de t->s?
    back_eps = set()
    for s in frag.pos:
        for t in s.trans.get(None, set()):
            back_eps.add((s, t))

    eps_edges, sym_edges = [], []
    left_col  = min(c for (c, _) in frag.pos.values())
    right_col = max(c for (c, _) in frag.pos.values())

    for s, (sc, sr) in frag.pos.items():
        p1 = _pt(sc, sr)
        for sym, nxts in s.trans.items():
            for t in nxts:
                tc, tr = frag.pos[t]
                p2 = _pt(tc, tr)
                is_eps = (sym is None)

                # misma fila
                if same_row(s, t):
                    sp = span(s, t)
                    # símbolo adyacente con ε-compañero → triángulo abajo
                    if (not is_eps) and sp == 1 and (t, s) in back_eps:
                        lane = lanes['down'][sr]; lanes['down'][sr] += 1
                        rad = base['down'] + lane * step
                        sym_edges.append(('curve_down', p1, p2, sym, rad))
                        continue
                    # ε largo → techo arriba
                    if is_eps and sp >= 2:
                        lane = lanes['roof'][sr]; lanes['roof'][sr] += 1
                        rad = base['roof'] + lane * step + abs(sp) * span_boost
                        # separa de loops up existentes
                        if up_used[sr]:
                            rad = max(rad, max(up_used[sr]) + gap)
                        roof_used[sr].append(rad)
                        eps_edges.append(('curve_up', p1, p2, 'ε', rad))
                        continue
                    # recta normal
                    if is_eps:
                        eps_edges.append(('line', p1, p2, 'ε'))
                    else:
                        sym_edges.append(('line', p1, p2, sym))
                    continue

                # bordes: S→A.start y A.accept→F (diagonal limpia)
                if sc == left_col and tc == left_col + 1:
                    (eps_edges if is_eps else sym_edges).append(('line', p1, p2, 'ε' if is_eps else sym))
                    continue
                if sc == right_col - 1 and tc == right_col:
                    (eps_edges if is_eps else sym_edges).append(('line', p1, p2, 'ε' if is_eps else sym))
                    continue

                # loop hacia atrás → arco arriba
                if tc < sc:
                    base_row = min(sr, tr)
                    lane = lanes['up'][base_row]; lanes['up'][base_row] += 1
                    rad = base['up'] + lane * step
                    if roof_used[base_row]:
                        rad = min(rad, min(roof_used[base_row]) - gap)
                        rad = max(rad, base['up'] * 0.6)
                    up_used[base_row].append(rad)
                    (eps_edges if is_eps else sym_edges).append(('curve_up', p1, p2, 'ε' if is_eps else sym, rad))
                    continue

                # caso general: línea con flecha
                (eps_edges if is_eps else sym_edges).append(('line', p1, p2, 'ε' if is_eps else sym))

    # dibujar: primero ε (debajo)
    for kind, *data in eps_edges:
        if kind == 'line':
            p1, p2, lab = data
            _line_arrow(ax, p1, p2, color=EPS_COLOR, lw=EPS_LW, z=2)
            mx, my = _mid(p1, p2); _label(ax, mx, my + 0.06, lab, EPS_COLOR, 3)
        elif kind == 'curve_up':
            p1, p2, lab, rad = data
            _arc_arrow(ax, p1, p2, up=True, rad=rad, color=EPS_COLOR, lw=EPS_LW, z=2)
            mx, my = _mid(p1, p2); _label(ax, mx, my + 0.08, lab, EPS_COLOR, 3)

    # luego símbolos (encima)
    for kind, *data in sym_edges:
        if kind == 'line':
            p1, p2, lab = data
            _line_arrow(ax, p1, p2, color=SYM_COLOR, lw=SYM_LW, z=5)
            mx, my = _mid(p1, p2); _label(ax, mx, my + 0.08, lab, SYM_COLOR, 6)
        elif kind == 'curve_up':
            p1, p2, lab, rad = data
            _arc_arrow(ax, p1, p2, up=True, rad=rad, color=SYM_COLOR, lw=SYM_LW, z=5)
            mx, my = _mid(p1, p2); _label(ax, mx, my + 0.10, lab, SYM_COLOR, 6)
        elif kind == 'curve_down':
            p1, p2, lab, rad = data
            _arc_arrow(ax, p1, p2, up=False, rad=rad, color=SYM_COLOR, lw=SYM_LW, z=5)
            mx, my = _mid(p1, p2); _label(ax, mx, my - 0.14, lab, SYM_COLOR, 6)

    # nodos
    R = 0.34
    acc = next(iter(frag.accepts))
    for s, (c, r) in frag.pos.items():
        x, y = _pt(c, r)
        face = "#ffd86b" if s is frag.start else ("#c6f5c3" if s is acc else "#cfe8ff")
        circ = Circle((x, y), R, facecolor=face, edgecolor="black", lw=1.5, zorder=8)
        ax.add_patch(circ)
        if s is acc:
            ax.add_patch(Circle((x, y), R + 0.07, facecolor="none", edgecolor="black", lw=1.4, zorder=7))
        ax.text(x, y, str(s.id), ha="center", va="center", fontsize=11, zorder=9)

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[draw] {out}")
