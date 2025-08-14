#Thompson desde postfix 
from __future__ import annotations
from typing import Dict, Set, List, Tuple, Optional

EPS = 'ε'

class State:
    _id_counter = 0
    @staticmethod
    def reset_ids():
        State._id_counter = 0
    def __init__(self):
        self.id: int = State._id_counter
        State._id_counter += 1
        self.trans: Dict[Optional[str], Set["State"]] = {}
    def add(self, sym: Optional[str], nxt: "State") -> None:
        self.trans.setdefault(sym, set()).add(nxt)
    def __repr__(self) -> str:
        return f"S{self.id}"

class Frag:
    def __init__(self, start: State, accepts: Set[State],
                 pos: Dict[State, Tuple[int, int]], width: int):
        self.start = start
        self.accepts = set(accepts)
        self.pos = pos
        self.width = width

def _shift(f: Frag, dcol: int, drow: int) -> Frag:
    pos2 = {s: (c + dcol, r + drow) for s, (c, r) in f.pos.items()}
    return Frag(f.start, f.accepts, pos2, f.width)

class Thompson:
    def __init__(self):
        State.reset_ids()

    def lit(self, a: str) -> Frag:
        s = State(); t = State()
        s.add(a, t)
        return Frag(s, {t}, {s: (0, 0), t: (1, 0)}, width=2)

    def eps(self) -> Frag:
        s = State(); t = State()
        s.add(None, t)
        return Frag(s, {t}, {s: (0, 0), t: (1, 0)}, width=2)

    def union(self, A: Frag, B: Frag) -> Frag:
        inner = max(A.width, B.width)
        A = _shift(A, 1 + (inner - A.width) // 2, -1)
        B = _shift(B, 1 + (inner - B.width) // 2, +1)
        S = State(); F = State()
        S.add(None, A.start); S.add(None, B.start)
        for a in A.accepts: a.add(None, F)
        for b in B.accepts: b.add(None, F)
        pos = {**A.pos, **B.pos, S: (0, 0), F: (inner + 1, 0)}
        return Frag(S, {F}, pos, width=inner + 2)

    def concat(self, A: Frag, B: Frag) -> Frag:
        B = _shift(B, A.width, 0)
        for a in A.accepts: a.add(None, B.start)
        return Frag(A.start, B.accepts, {**A.pos, **B.pos}, width=A.width + B.width)

    def star(self, A: Frag) -> Frag:
        A = _shift(A, 1, +1)  
        S = State(); F = State()
        S.add(None, A.start); S.add(None, F)
        for a in A.accepts:
            a.add(None, A.start); a.add(None, F)
        pos = {**A.pos, S: (0, 0), F: (A.width + 1, 0)}
        return Frag(S, {F}, pos, width=A.width + 2)

    def plus(self, A: Frag) -> Frag:
        A = _shift(A, 1, +1)  
        S = State(); F = State()
        S.add(None, A.start)
        for a in A.accepts:
            a.add(None, A.start); a.add(None, F)
        pos = {**A.pos, S: (0, 0), F: (A.width + 1, 0)}
        return Frag(S, {F}, pos, width=A.width + 2)

    def optional(self, A: Frag) -> Frag:
        A = _shift(A, 1, +1)  
        S = State(); F = State()
        S.add(None, A.start); S.add(None, F)
        for a in A.accepts: a.add(None, F)
        pos = {**A.pos, S: (0, 0), F: (A.width + 1, 0)}
        return Frag(S, {F}, pos, width=A.width + 2)

    def from_postfix(self, tokens: List[str]) -> Frag:
        st: List[Frag] = []
        for tok in tokens:
            if tok == '.':
                b = st.pop(); a = st.pop(); st.append(self.concat(a, b))
            elif tok == '|':
                b = st.pop(); a = st.pop(); st.append(self.union(a, b))
            elif tok == '*':
                a = st.pop(); st.append(self.star(a))
            elif tok == '+':
                a = st.pop(); st.append(self.plus(a))
            elif tok == '?':
                a = st.pop(); st.append(self.optional(a))
            elif tok in {'ε', 'eps'}:
                st.append(self.eps())
            else:
                sym = tok[1] if (len(tok) == 2 and tok[0] == '\\') else tok
                st.append(self.lit(sym))
        if len(st) != 1:
            raise ValueError("Postfix mal formado")
        return st.pop()

def renumber_left_to_right(frag: Frag) -> None:
    accept = next(iter(frag.accepts))
    others = [s for s in frag.pos if s not in (frag.start, accept)]
    others.sort(key=lambda s: (frag.pos[s][1], frag.pos[s][0]))
    ordered = [frag.start] + others + [accept]
    for new_id, s in enumerate(ordered):
        s.id = new_id

def epsilon_closure(states: Set[State]) -> Set[State]:
    stack = list(states); out = set(states)
    while stack:
        s = stack.pop()
        for nxt in s.trans.get(None, set()):
            if nxt not in out:
                out.add(nxt); stack.append(nxt)
    return out

def move(states: Set[State], sym: str) -> Set[State]:
    out: Set[State] = set()
    for s in states:
        for nxt in s.trans.get(sym, set()): out.add(nxt)
    return out

def accepts(frag: Frag, w: str) -> bool:
    cur = epsilon_closure({frag.start})
    for ch in w:
        cur = epsilon_closure(move(cur, ch))
    return next(iter(frag.accepts)) in cur
