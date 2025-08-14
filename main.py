from pathlib import Path
from regex_tools import to_postfix_tokens
from nfa_core import Thompson, Frag, accepts, renumber_left_to_right
from draw_ortho import draw_fragment_ortho

OUT_DIR = Path("afn_outputs")
OUT_DIR.mkdir(exist_ok=True)

DEBUG_EDGES = False 

def dump_symbol_edges(frag: Frag):
    out = []
    for s in frag.pos:
        for sym, nxts in s.trans.items():
            if sym is not None:
                for t in nxts:
                    out.append((s.id, t.id, sym))
    return out

def run_file(path="regex_p1.txt"):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            r = line.strip()
            if not r:
                continue
            print("\n" + "="*70)
            print(f"[{i}] Regex (infijo): {r}")
            tokens = to_postfix_tokens(r)
            print("Postfix:", tokens)

            th = Thompson()
            frag: Frag = th.from_postfix(tokens)

            # renumerar: start=0, accept=último, resto por (fila, col)
            renumber_left_to_right(frag)

            if DEBUG_EDGES:
                print("Aristas con símbolo:", dump_symbol_edges(frag))

            png = OUT_DIR / f"afn_{i}.png"
            draw_fragment_ortho(frag, str(png))

            print(f"\n Autómata generado: {png}")
            print("─" * 60)
            while True:
                print("Ingrese una cadena w para verificar si pertenece al lenguaje,\n o presione ENTER para continuar con la siguiente expresión:")
                w = input(" w =   ")
                if w == "":
                    break
                result = "SÍ" if accepts(frag, w) else "NO"
                print(f"   Resultado: {result}")
                print()

if __name__ == "__main__":
    run_file()
