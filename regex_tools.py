from typing import List, Tuple

PREC = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
LEFT_ASSOC = {'.', '|'}          # asociativos a la izquierda
RIGHT_ASSOC = {'*', '+', '?'}    # unarios, asociativos a la derecha

def _next_token(s: str, i: int) -> Tuple[str, int]:
    if i >= len(s):
        return '', i
    c = s[i]
    if c == '\\' and i + 1 < len(s):
        return s[i:i+2], i + 2
    return c, i + 1

def _is_operand(tok: str) -> bool:
    """Operando: letra/dígito, ε, o literal escapado."""
    if tok == 'ε':
        return True
    if len(tok) == 2 and tok[0] == '\\':
        return True
    return len(tok) == 1 and tok.isalnum()

def _should_concat(left_tok: str, right_tok: str) -> bool:
    left_ok = _is_operand(left_tok) or left_tok in {')', '*', '+', '?'}
    right_ok = _is_operand(right_tok) or right_tok in {'('}
    return left_ok and right_ok

def tokenize_with_concatenation(regex: str) -> List[str]:
    tokens: List[str] = []
    i = 0
    raw: List[str] = []
    while i < len(regex):
        if regex[i].isspace():
            i += 1
            continue
        tok, i = _next_token(regex, i)
        raw.append(tok)
    for j, tok in enumerate(raw):
        tokens.append(tok)
        if j + 1 < len(raw):
            nxt = raw[j + 1]
            if _should_concat(tok, nxt):
                tokens.append('.')
    return tokens

def shunting_yard_tokens(tokens: List[str]) -> List[str]:
    output: List[str] = []
    stack: List[str] = []

    for tok in tokens:
        if _is_operand(tok):
            output.append(tok)
        elif tok == '(':
            stack.append(tok)
        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Paréntesis desbalanceados")
            stack.pop()  # descartar '('
        elif tok in PREC:
            while (stack and stack[-1] in PREC and
                   (PREC[stack[-1]] > PREC[tok] or
                   (PREC[stack[-1]] == PREC[tok] and tok in LEFT_ASSOC))):
                output.append(stack.pop())
            stack.append(tok)
        else:
            raise ValueError(f"Token desconocido: {tok}")

    while stack:
        top = stack.pop()
        if top in {'(', ')'}:
            raise ValueError("Paréntesis desbalanceados al final")
        output.append(top)

    return output

def to_postfix_tokens(regex: str) -> List[str]:
    with_dots = tokenize_with_concatenation(regex)
    return shunting_yard_tokens(with_dots)
