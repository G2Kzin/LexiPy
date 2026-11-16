"""Analisador sintático recursivo descendente para o subconjunto didático do LexiPy.

A entrada é validada pelo scanner léxico existente antes de chegar ao parser.
A AST é representada por dicionários serializáveis em JSON.
"""
from __future__ import annotations

import io
import tokenize
from typing import Any


class ErroSintatico(Exception):
    def __init__(self, mensagem: str, linha: int, coluna: int):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna


class Parser:
    BINARIOS = {
        "or": (1, "OU"), "and": (2, "E"),
        "==": (3, "IGUAL"), "!=": (3, "DIFERENTE"),
        "<": (3, "MENOR"), "<=": (3, "MENOR_IGUAL"),
        ">": (3, "MAIOR"), ">=": (3, "MAIOR_IGUAL"),
        "in": (3, "EM"), "is": (3, "IDENTIDADE"),
        "+": (4, "SOMA"), "-": (4, "SUBTRACAO"),
        "*": (5, "MULTIPLICACAO"), "/": (5, "DIVISAO"),
        "//": (5, "DIVISAO_INTEIRA"), "%": (5, "RESTO"),
        "**": (6, "POTENCIA"),
    }

    def __init__(self, codigo: str):
        self.tokens = []
        ignorados = {tokenize.ENCODING, tokenize.NL, tokenize.COMMENT,
                     tokenize.INDENT, tokenize.DEDENT}
        try:
            for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
                if tok.type in ignorados:
                    continue
                if tok.type == tokenize.ENDMARKER:
                    self.tokens.append(tok)
                    break
                self.tokens.append(tok)
        except (tokenize.TokenError, IndentationError) as exc:
            detalhe = exc.args[0] if exc.args else "Erro de tokenização."
            pos = exc.args[1] if len(exc.args) > 1 and isinstance(exc.args[1], tuple) else (1, 0)
            raise ErroSintatico(str(detalhe), pos[0], pos[1] + 1) from exc
        self.i = 0

    def atual(self):
        return self.tokens[min(self.i, len(self.tokens) - 1)]

    def valor(self):
        return self.atual().string

    def avancar(self):
        tok = self.atual()
        if tok.type != tokenize.ENDMARKER:
            self.i += 1
        return tok

    def aceitar(self, valor):
        if self.valor() == valor:
            return self.avancar()
        return None

    def exigir(self, valor, mensagem=None):
        tok = self.aceitar(valor)
        if tok is None:
            atual = self.atual()
            raise ErroSintatico(mensagem or f"Esperado {valor!r}, encontrado {atual.string or 'fim do código'!r}.",
                                atual.start[0], atual.start[1] + 1)
        return tok

    def exigir_tipo(self, tipo, descricao):
        tok = self.atual()
        if tok.type != tipo:
            raise ErroSintatico(f"Esperado {descricao}, encontrado {tok.string or 'fim do código'!r}.",
                                tok.start[0], tok.start[1] + 1)
        return self.avancar()

    def nova_linha(self):
        while self.atual().type in (tokenize.NL,):
            self.avancar()
        if self.atual().type == tokenize.NEWLINE:
            self.avancar()

    def programa(self):
        corpo = []
        while self.atual().type != tokenize.ENDMARKER:
            if self.atual().type == tokenize.NEWLINE:
                self.avancar()
                continue
            corpo.append(self.comando())
        return {"tipo": "Programa", "corpo": corpo}

    def comando(self):
        if self.valor() == "if":
            return self.condicional()
        if self.valor() == "while":
            return self.laco_while()
        if self.valor() == "for":
            return self.laco_for()
        return self.comando_simples()

    def suite(self):
        self.exigir(":")
        if self.atual().type != tokenize.NEWLINE:
            # Suite simples na mesma linha.
            comandos = [self.comando_simples()]
            while self.aceitar(";"):
                if self.atual().type in (tokenize.NEWLINE, tokenize.ENDMARKER):
                    break
                comandos.append(self.comando_simples())
            self.nova_linha()
            return comandos
        self.avancar()
        if self.atual().type != tokenize.INDENT:
            tok = self.atual()
            raise ErroSintatico("Esperado um bloco indentado após ':'.", tok.start[0], tok.start[1] + 1)
        self.avancar()
        comandos = []
        while self.atual().type not in (tokenize.DEDENT, tokenize.ENDMARKER):
            if self.atual().type == tokenize.NEWLINE:
                self.avancar()
                continue
            comandos.append(self.comando())
        if self.atual().type == tokenize.DEDENT:
            self.avancar()
        return comandos

    def condicional(self):
        self.exigir("if")
        condicao = self.expressao()
        corpo = self.suite()
        alternativa = []
        if self.aceitar("else"):
            alternativa = self.suite()
        return {"tipo": "Condicional", "condicao": condicao,
                "corpo": corpo, "alternativa": alternativa}

    def laco_while(self):
        self.exigir("while")
        condicao = self.expressao()
        return {"tipo": "Enquanto", "condicao": condicao, "corpo": self.suite()}

    def laco_for(self):
        self.exigir("for")
        alvo = self.exigir_tipo(tokenize.NAME, "identificador")
        self.exigir("in", "Esperado 'in' após a variável do laço.")
        iteravel = self.expressao()
        return {"tipo": "ParaCada", "alvo": alvo.string,
                "iteravel": iteravel, "corpo": self.suite()}

    def comando_simples(self):
        if self.valor() in ("pass", "break", "continue"):
            palavra = self.avancar().string
            self.nova_linha()
            return {"tipo": palavra.capitalize()}
        if self.valor() == "return":
            self.avancar()
            valor = None if self.atual().type == tokenize.NEWLINE else self.expressao()
            self.nova_linha()
            return {"tipo": "Retorno", "valor": valor}

        expr = self.expressao()
        if self.valor() in ("=", "+=", "-=", "*=", "/=", "//=", "%=", "**="):
            op = self.avancar().string
            if expr.get("tipo") != "Identificador":
                tok = self.atual()
                raise ErroSintatico("O lado esquerdo da atribuição deve ser um identificador.",
                                    tok.start[0], tok.start[1] + 1)
            valor = self.expressao()
            self.nova_linha()
            return {"tipo": "Atribuicao", "alvo": expr["nome"], "operador": op, "valor": valor}
        self.nova_linha()
        return {"tipo": "Expressao", "expressao": expr}

    def expressao(self, minimo=0):
        esquerda = self.prefixo()
        while True:
            op = self.valor()
            if op == "not" and minimo <= 2:
                break
            info = self.BINARIOS.get(op)
            if info is None or info[0] < minimo:
                break
            precedencia, nome = info
            self.avancar()
            direita = self.expressao(precedencia if op == "**" else precedencia + 1)
            esquerda = {"tipo": "Binaria", "operador": nome,
                        "esquerda": esquerda, "direita": direita}
        return esquerda

    def prefixo(self):
        tok = self.atual()
        if tok.string in ("+", "-", "not"):
            op = self.avancar().string
            return {"tipo": "Unaria", "operador": op, "operando": self.expressao(6)}
        if tok.type == tokenize.NUMBER:
            self.avancar()
            return {"tipo": "Numero", "valor": tok.string}
        if tok.type == tokenize.STRING:
            self.avancar()
            return {"tipo": "Texto", "valor": tok.string}
        if tok.string in ("True", "False", "None"):
            self.avancar()
            return {"tipo": "Literal", "valor": tok.string}
        if tok.type == tokenize.NAME:
            self.avancar()
            no = {"tipo": "Identificador", "nome": tok.string}
            while True:
                if self.aceitar("("):
                    argumentos = []
                    if self.valor() != ")":
                        argumentos.append(self.expressao())
                        while self.aceitar(","):
                            if self.valor() == ")":
                                break
                            argumentos.append(self.expressao())
                    self.exigir(")")
                    no = {"tipo": "Chamada", "funcao": no, "argumentos": argumentos}
                elif self.aceitar("["):
                    indice = self.expressao()
                    self.exigir("]")
                    no = {"tipo": "Indice", "objeto": no, "indice": indice}
                elif self.aceitar("."):
                    atributo = self.exigir_tipo(tokenize.NAME, "nome do atributo")
                    no = {"tipo": "Atributo", "objeto": no, "nome": atributo.string}
                else:
                    break
            return no
        if self.aceitar("("):
            expr = self.expressao()
            self.exigir(")")
            return expr
        if self.aceitar("["):
            itens = []
            if self.valor() != "]":
                itens.append(self.expressao())
                while self.aceitar(","):
                    if self.valor() == "]":
                        break
                    itens.append(self.expressao())
            self.exigir("]")
            return {"tipo": "Lista", "itens": itens}
        if self.aceitar("{"):
            pares = []
            if self.valor() != "}":
                while True:
                    chave = self.expressao()
                    self.exigir(":")
                    valor = self.expressao()
                    pares.append({"chave": chave, "valor": valor})
                    if not self.aceitar(","):
                        break
                    if self.valor() == "}":
                        break
            self.exigir("}")
            return {"tipo": "Dicionario", "pares": pares}
        raise ErroSintatico(f"Expressão inesperada: {tok.string or 'fim do código'!r}.",
                            tok.start[0], tok.start[1] + 1)


def parse(codigo: str) -> dict[str, Any]:
    """Analisa sintaticamente o subconjunto suportado e retorna uma AST."""
    parser = Parser(codigo)
    arvore = parser.programa()
    return {"sucesso": True, "ast": arvore, "erros": []}
