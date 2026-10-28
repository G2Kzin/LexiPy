"""Scanner léxico didático para um subconjunto documentado de Python.

Não executa o código-fonte. Reconhece lexemas, categorias e posições.
"""
from __future__ import annotations

import keyword
import re
from typing import Any

PYTHON_KEYWORDS = set(keyword.kwlist)
BOOLEAN_LITERALS = {"True", "False", "None"}

# Operadores compostos vêm antes dos operadores de um caractere.
OPERATORS = [
    "**=", "//=", "==", "!=", "<=", ">=", "**", "//", "+=", "-=",
    "*=", "/=", "%=", "->", "=", "+", "-", "*", "/", "%", "<", ">",
]
DELIMITERS = set("()[]{}:,.;")
LOGICAL_OPERATORS = {"and", "or", "not"}
RELATIONAL_WORD_OPERATORS = {"in", "is"}

def scan(codigo: str) -> dict[str, Any]:
    """Tokeniza código Python do subconjunto LexiPy e acumula erros léxicos."""
    tokens: list[dict[str, Any]] = []
    erros: list[dict[str, Any]] = []
    i, linha, coluna = 0, 1, 1
    n = len(codigo)

    def advance_char(ch: str) -> None:
        nonlocal linha, coluna
        if ch == "\n":
            linha += 1
            coluna = 1
        else:
            coluna += 1

    def add_token(tipo: str, lexema: str, l: int, c: int) -> None:
        tokens.append({"tipo": tipo, "lexema": lexema, "linha": l, "coluna": c})

    def add_error(lexema: str, l: int, c: int, mensagem: str) -> None:
        erros.append({
            "tipo": "ERRO_LEXICO", "lexema": lexema,
            "linha": l, "coluna": c, "mensagem": mensagem
        })

    while i < n:
        ch = codigo[i]

        # Espaços em branco são ignorados, mas atualizam as posições.
        if ch in " \t\r\f":
            advance_char(ch)
            i += 1
            continue
        if ch == "\n":
            advance_char(ch)
            i += 1
            continue

        start_i, start_line, start_col = i, linha, coluna

        # Comentários Python: do caractere # até o fim da linha.
        if ch == "#":
            while i < n and codigo[i] != "\n":
                advance_char(codigo[i])
                i += 1
            continue

        # Strings simples/de aspas duplas; strings triplas não fazem parte do escopo.
        if ch in ("'", '"'):
            quote = ch
            if codigo.startswith(quote * 3, i):
                lexema = quote * 3
                add_error(lexema, linha, coluna,
                          "Strings com aspas triplas não fazem parte do subconjunto suportado.")
                for _ in range(3):
                    advance_char(codigo[i]); i += 1
                continue

            advance_char(ch)
            i += 1
            escaped = False
            closed = False
            while i < n:
                current = codigo[i]
                if current == "\n" and not escaped:
                    break
                if escaped:
                    escaped = False
                    advance_char(current)
                    i += 1
                    continue
                if current == "\\":
                    escaped = True
                    advance_char(current)
                    i += 1
                    continue
                if current == quote:
                    advance_char(current)
                    i += 1
                    closed = True
                    break
                advance_char(current)
                i += 1

            lexema = codigo[start_i:i]
            if closed:
                add_token("LITERAL_STRING", lexema, start_line, start_col)
            else:
                add_error(lexema, start_line, start_col,
                          "String não terminada. Feche o literal com aspas na mesma linha.")
            continue

        # Identificadores e palavras reservadas (subconjunto ASCII documentado).
        if ch.isascii() and (ch.isalpha() or ch == "_"):
            i += 1
            advance_char(ch)
            while i < n and codigo[i].isascii() and (codigo[i].isalnum() or codigo[i] == "_"):
                advance_char(codigo[i])
                i += 1
            lexema = codigo[start_i:i]
            if lexema in BOOLEAN_LITERALS:
                tipo = "LITERAL_BOOLEANO"
            elif lexema in PYTHON_KEYWORDS:
                if lexema in LOGICAL_OPERATORS:
                    tipo = "OPERADOR_LOGICO"
                elif lexema in RELATIONAL_WORD_OPERATORS:
                    tipo = "OPERADOR_RELACIONAL"
                else:
                    tipo = "PALAVRA_RESERVADA"
            else:
                tipo = "IDENTIFICADOR"
            add_token(tipo, lexema, start_line, start_col)
            continue

        # Literais numéricos inteiros e reais decimais, sem expoente/sufixos.
        if ch.isdigit() and ch.isascii():
            i += 1
            advance_char(ch)
            while i < n and codigo[i].isascii() and codigo[i].isdigit():
                advance_char(codigo[i])
                i += 1
            is_real = False
            if i + 1 < n and codigo[i] == "." and codigo[i + 1].isascii() and codigo[i + 1].isdigit():
                is_real = True
                advance_char(codigo[i]); i += 1
                while i < n and codigo[i].isascii() and codigo[i].isdigit():
                    advance_char(codigo[i])
                    i += 1
            lexema = codigo[start_i:i]
            add_token("LITERAL_REAL" if is_real else "LITERAL_INTEIRO",
                      lexema, start_line, start_col)
            continue

        # Operadores: testar os maiores primeiro.
        operator = next((op for op in OPERATORS if codigo.startswith(op, i)), None)
        if operator:
            for current in operator:
                advance_char(current)
            i += len(operator)
            if operator in {"==", "!=", "<", ">", "<=", ">=", "in", "is"}:
                tipo = "OPERADOR_RELACIONAL"
            elif operator in {"=", "+=", "-=", "*=", "/=", "%=", "**=", "//="}:
                tipo = "OPERADOR_ATRIBUICAO"
            elif operator == "->":
                tipo = "OPERADOR"
            else:
                tipo = "OPERADOR_ARITMETICO"
            add_token(tipo, operator, start_line, start_col)
            continue

        if ch in DELIMITERS:
            advance_char(ch)
            i += 1
            add_token("DELIMITADOR", ch, start_line, start_col)
            continue

        # Qualquer caractere fora do escopo gera erro e a leitura continua.
        advance_char(ch)
        i += 1
        add_error(ch, start_line, start_col,
                  f"Caractere não reconhecido: {ch!r}. Verifique o subconjunto Python suportado.")

    return {"sucesso": len(erros) == 0, "tokens": tokens, "erros": erros}
