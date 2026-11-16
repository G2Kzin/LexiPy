"""Parser recursivo descendente do subconjunto sintatico do LexiPy."""
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
           "//": (5, "DIVISAO_INTEIRA"), "%": (5, "RESTO"), "**": (6, "POTENCIA")}

    def __init__(self, codigo):
        self.ts = []
        try:
            for t in tokenize.generate_tokens(io.StringIO(codigo).readline):
                if t.type not in (tokenize.ENCODING, tokenize.NL, tokenize.COMMENT):
                    self.ts.append(t)
        except (tokenize.TokenError, IndentationError) as e:
            pos = e.args[1] if len(e.args) > 1 and isinstance(e.args[1], tuple) else (1, 0)
            raise ErroSintatico(str(e.args[0]), pos[0], pos[1] + 1) from e
        self.i = 0

    def t(self):
        return self.ts[min(self.i, len(self.ts)-1)]

    def v(self):
        return self.t().string

    def pop(self):
        t = self.t()
        if t.type != tokenize.ENDMARKER:
            self.i += 1
        return t

    def accept(self, s):
        return self.pop() if self.v() == s else None

    def need(self, s, msg=None):
        t = self.accept(s)
        if t is None:
            a = self.t()
            raise ErroSintatico(msg or f"Esperado {s!r}; encontrado {a.string or 'fim do código'!r}.", a.start[0], a.start[1]+1)
        return t

    def need_type(self, typ, desc):
        t = self.t()
        if t.type != typ:
            raise ErroSintatico(f"Esperado {desc}; encontrado {t.string or 'fim do código'!r}.", t.start[0], t.start[1]+1)
        return self.pop()

    def newline(self):
        if self.t().type == tokenize.NEWLINE:
            self.pop()

    def program(self):
        body = []
        while self.t().type != tokenize.ENDMARKER:
            if self.t().type in (tokenize.NEWLINE, tokenize.DEDENT):
                self.pop()
            else:
                body.append(self.statement())
        return {"tipo": "Programa", "corpo": body}

    def statement(self):
        if self.v() == "if":
            self.pop()
            cond = self.expr()
            body = self.suite()
            other = self.suite() if self.accept("else") else []
            return {"tipo": "Condicional", "condicao": cond, "corpo": body, "alternativa": other}
        if self.v() == "while":
            self.pop()
            return {"tipo": "Enquanto", "condicao": self.expr(), "corpo": self.suite()}
        if self.v() == "for":
            self.pop()
            target = self.need_type(tokenize.NAME, "identificador").string
            self.need("in", "Esperado 'in' após a variável do laço.")
            return {"tipo": "ParaCada", "alvo": target, "iteravel": self.expr(), "corpo": self.suite()}
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
            t = self.t()
            raise ErroSintatico("Esperado bloco indentado após ':'.", t.start[0], t.start[1]+1)
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
        if self.v() in ("pass", "break", "continue"):
            word = self.pop().string
            self.newline()
            return {"tipo": word.capitalize()}
        if self.v() == "return":
            self.pop()
            value = None if self.t().type == tokenize.NEWLINE else self.expr()
            self.newline()
            return {"tipo": "Retorno", "valor": value}
        left = self.expr()
        if self.v() in ("=", "+=", "-=", "*=", "/=", "//=", "%=", "**="):
            op = self.pop().string
            if left["tipo"] != "Identificador":
                t = self.t()
                raise ErroSintatico("Alvo de atribuição inválido.", t.start[0], t.start[1]+1)
            right = self.expr()
            self.newline()
            return {"tipo": "Atribuicao", "alvo": left["nome"], "operador": op, "valor": right}
        self.newline()
        return {"tipo": "Expressao", "expressao": left}

    def expr(self, minp=0):
        left = self.prefix()
        while self.v() in self.BIN and self.BIN[self.v()][0] >= minp:
            op = self.pop().string
            prec, name = self.BIN[op]
            right = self.expr(prec if op == "**" else prec+1)
            left = {"tipo": "Binaria", "operador": name, "esquerda": left, "direita": right}
        return left

    def prefix(self):
        t = self.t()
        if t.string in ("+", "-", "not"):
            op = self.pop().string
            return {"tipo": "Unaria", "operador": op, "operando": self.expr(6)}
        if t.type == tokenize.NUMBER:
            self.pop()
            return {"tipo": "Numero", "valor": t.string}
        if t.type == tokenize.STRING:
            self.pop()
            return {"tipo": "Texto", "valor": t.string}
        if t.string in ("True", "False", "None"):
            self.pop()
            return {"tipo": "Literal", "valor": t.string}
        if t.type == tokenize.NAME:
            self.pop()
            node = {"tipo": "Identificador", "nome": t.string}
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
                    node = {"tipo": "Chamada", "funcao": node, "argumentos": args}
                elif self.accept("["):
                    idx = self.expr()
                    self.need("]")
                    node = {"tipo": "Indice", "objeto": node, "indice": idx}
                elif self.accept("."):
                    attr = self.need_type(tokenize.NAME, "atributo").string
                    node = {"tipo": "Atributo", "objeto": node, "nome": attr}
                else:
                    return node
        if self.accept("("):
            node = self.expr()
            self.need(")")
            return node
        if self.accept("["):
            items = []
            if self.v() != "]":
                items.append(self.expr())
                while self.accept(","):
                    if self.v() == "]":
                        break
                    items.append(self.expr())
            self.need("]")
            return {"tipo": "Lista", "itens": items}
        t = self.t()
        raise ErroSintatico(f"Expressão inesperada: {t.string or 'fim do código'!r}.", t.start[0], t.start[1]+1)


def parse(codigo):
    return {"sucesso": True, "ast": Parser(codigo).program(), "erros": []}
