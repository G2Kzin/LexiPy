"""Parser recursivo descendente para o subconjunto didático do LexiPy."""
import io
import tokenize


class ErroSintatico(Exception):
    def __init__(self, mensagem, linha, coluna):
        super().__init__(mensagem)
        self.mensagem, self.linha, self.coluna = mensagem, linha, coluna


class Parser:
    BIN = {"or": (1, "OU"), "and": (2, "E"), "==": (3, "IGUAL"),
           "!=": (3, "DIFERENTE"), "<": (3, "MENOR"), "<=": (3, "MENOR_IGUAL"),
           ">": (3, "MAIOR"), ">=": (3, "MAIOR_IGUAL"), "in": (3, "EM"),
           "is": (3, "IDENTIDADE"), "+": (4, "SOMA"), "-": (4, "SUBTRACAO"),
           "*": (5, "MULTIPLICACAO"), "/": (5, "DIVISAO"),
           "//": (5, "DIVISAO_INTEIRA"), "%": (5, "RESTO"), "**": (7, "POTENCIA")}

    def __init__(self, codigo):
        self.ts = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
                if tok.type not in (tokenize.ENCODING, tokenize.NL, tokenize.COMMENT):
                    self.ts.append(tok)
        except (tokenize.TokenError, IndentationError) as exc:
            pos = exc.args[1] if len(exc.args) > 1 and isinstance(exc.args[1], tuple) else (1, 0)
            raise ErroSintatico(str(exc.args[0]), pos[0], pos[1] + 1) from exc
        if not self.ts or self.ts[-1].type != tokenize.ENDMARKER:
            raise ErroSintatico("Fim inesperado da entrada.", 1, 1)
        self.i = 0

    @staticmethod
    def node(tipo, tok, **attrs):
        return {"tipo": tipo, "linha": tok.start[0], "coluna": tok.start[1] + 1, **attrs}

    def t(self):
        return self.ts[min(self.i, len(self.ts) - 1)]

    def v(self):
        return self.t().string

    def pop(self):
        tok = self.t()
        if tok.type != tokenize.ENDMARKER:
            self.i += 1
        return tok

    def accept(self, value):
        return self.pop() if self.v() == value else None

    def need(self, value, message=None):
        tok = self.accept(value)
        if tok is None:
            cur = self.t()
            raise ErroSintatico(message or f"Esperado {value!r}; encontrado {cur.string or 'fim do código'!r}.",
                                cur.start[0], cur.start[1] + 1)
        return tok

    def need_type(self, typ, description):
        tok = self.t()
        if tok.type != typ:
            raise ErroSintatico(f"Esperado {description}; encontrado {tok.string or 'fim do código'!r}.",
                                tok.start[0], tok.start[1] + 1)
        return self.pop()

    def newline(self):
        if self.t().type == tokenize.NEWLINE:
            self.pop()

    def program(self):
        first = self.t()
        body = []
        while self.t().type != tokenize.ENDMARKER:
            if self.t().type in (tokenize.NEWLINE, tokenize.DEDENT):
                self.pop()
            else:
                body.append(self.statement())
        return self.node("Programa", first, corpo=body)

    def statement(self):
        if self.v() == "if":
            start = self.pop()
            condition = self.expr()
            body = self.suite()
            other = self.suite() if self.accept("else") else []
            return self.node("Condicional", start, condicao=condition, corpo=body, alternativa=other)
        if self.v() == "while":
            start = self.pop()
            condition = self.expr()
            return self.node("Enquanto", start, condicao=condition, corpo=self.suite())
        if self.v() == "for":
            start = self.pop()
            target = self.need_type(tokenize.NAME, "identificador").string
            self.need("in", "Esperado 'in' após a variável do laço.")
            iterable = self.expr()
            return self.node("ParaCada", start, alvo=target, iteravel=iterable, corpo=self.suite())
        return self.simple()

    def suite(self):
        self.need(":")
        if self.t().type != tokenize.NEWLINE:
            body = [self.simple()]
            while self.accept(";"):
                if self.t().type in (tokenize.NEWLINE, tokenize.ENDMARKER):
                    break
                body.append(self.simple())
            self.newline()
            return body
        self.pop()
        if self.t().type != tokenize.INDENT:
            tok = self.t()
            raise ErroSintatico("Esperado bloco indentado após ':'.", tok.start[0], tok.start[1] + 1)
        self.pop()
        body = []
        while self.t().type not in (tokenize.DEDENT, tokenize.ENDMARKER):
            if self.t().type == tokenize.NEWLINE:
                self.pop()
            else:
                body.append(self.statement())
        if self.t().type == tokenize.DEDENT:
            self.pop()
        return body

    def simple(self):
        start = self.t()
        if self.v() in ("pass", "break", "continue"):
            word = self.pop().string
            self.newline()
            return self.node(word.capitalize(), start)
        if self.v() == "return":
            self.pop()
            value = None if self.t().type == tokenize.NEWLINE else self.expr()
            self.newline()
            return self.node("Retorno", start, valor=value)
        left = self.expr()
        if self.v() in ("=", "+=", "-=", "*=", "/=", "//=", "%=", "**="):
            op = self.pop().string
            if left["tipo"] != "Identificador":
                tok = self.t()
                raise ErroSintatico("Alvo de atribuição inválido.", tok.start[0], tok.start[1] + 1)
            right = self.expr()
            self.newline()
            return self.node("Atribuicao", start, alvo=left["nome"], operador=op, valor=right)
        self.newline()
        return self.node("Expressao", start, expressao=left)

    def expr(self, minp=0):
        left = self.prefix()
        while self.v() in self.BIN and self.BIN[self.v()][0] >= minp:
            op_tok = self.pop()
            op = op_tok.string
            prec, name = self.BIN[op]
            # Potência associa à direita; os demais operadores à esquerda.
            right = self.expr(prec if op == "**" else prec + 1)
            left = self.node("Binaria", op_tok, operador=name, esquerda=left, direita=right)
        return left

    def prefix(self):
        tok = self.t()
        if tok.string in ("+", "-", "not"):
            op = self.pop().string
            # not tem precedência menor que comparações; sinais têm precedência alta.
            operand = self.expr(3 if op == "not" else 6)
            return self.node("Unaria", tok, operador=op, operando=operand)
        if tok.type == tokenize.NUMBER:
            self.pop()
            return self.node("Numero", tok, valor=tok.string)
        if tok.type == tokenize.STRING:
            self.pop()
            return self.node("Texto", tok, valor=tok.string)
        if tok.string in ("True", "False", "None"):
            self.pop()
            return self.node("Literal", tok, valor=tok.string)
        if tok.type == tokenize.NAME:
            self.pop()
            node = self.node("Identificador", tok, nome=tok.string)
            while True:
                if self.accept("("):
                    args = []
                    if self.v() != ")":
                        args.append(self.expr())
                        while self.accept(","):
                            if self.v() == ")":
                                break
                            args.append(self.expr())
                    self.need(")")
                    node = self.node("Chamada", tok, funcao=node, argumentos=args)
                elif self.accept("["):
                    index = self.expr()
                    self.need("]")
                    node = self.node("Indice", tok, objeto=node, indice=index)
                elif self.accept("."):
                    attr = self.need_type(tokenize.NAME, "nome do atributo").string
                    node = self.node("Atributo", tok, objeto=node, nome=attr)
                else:
                    break
            return node
        if self.accept("("):
            expr = self.expr()
            self.need(")")
            return expr
        if self.accept("["):
            items = []
            if self.v() != "]":
                items.append(self.expr())
                while self.accept(","):
                    if self.v() == "]":
                        break
                    items.append(self.expr())
            self.need("]")
            return self.node("Lista", tok, itens=items)
        raise ErroSintatico(f"Expressão inesperada: {tok.string or 'fim do código'!r}.",
                            tok.start[0], tok.start[1] + 1)


def parse(codigo):
    return {"sucesso": True, "ast": Parser(codigo).program(), "erros": []}
