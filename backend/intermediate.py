"""Gerador didático de código intermediário de três endereços a partir da AST."""
from __future__ import annotations


class GeradorCodigoIntermediario:
    OPERADORES = {
        "SOMA": "+", "SUBTRACAO": "-", "MULTIPLICACAO": "*",
        "DIVISAO": "/", "DIVISAO_INTEIRA": "//", "RESTO": "%",
        "POTENCIA": "**", "IGUAL": "==", "DIFERENTE": "!=",
        "MENOR": "<", "MENOR_IGUAL": "<=", "MAIOR": ">",
        "MAIOR_IGUAL": ">=", "OU": "or", "E": "and",
        "EM": "in", "IDENTIDADE": "is",
    }

    def __init__(self):
        self.linhas = []
        self.temp = 0
        self.rotulo = 0

    def emitir(self, texto):
        self.linhas.append(texto)

    def temporario(self):
        self.temp += 1
        return f"t{self.temp}"

    def novo_rotulo(self, prefixo="L"):
        self.rotulo += 1
        return f"{prefixo}{self.rotulo}"

    def expressao(self, node):
        tipo = node["tipo"]
        if tipo in ("Numero", "Texto", "Literal"):
            return str(node["valor"])
        if tipo == "Identificador":
            return node["nome"]
        if tipo == "Binaria":
            esquerda = self.expressao(node["esquerda"])
            direita = self.expressao(node["direita"])
            resultado = self.temporario()
            operador = self.OPERADORES.get(node["operador"], node["operador"])
            self.emitir(f"{resultado} = {esquerda} {operador} {direita}")
            return resultado
        if tipo == "Unaria":
            valor = self.expressao(node["operando"])
            resultado = self.temporario()
            self.emitir(f"{resultado} = {node['operador']} {valor}")
            return resultado
        if tipo == "Chamada":
            funcao = self.expressao(node["funcao"])
            args = [self.expressao(arg) for arg in node["argumentos"]]
            resultado = self.temporario()
            self.emitir(f"{resultado} = call {funcao}({', '.join(args)})")
            return resultado
        if tipo == "Lista":
            itens = [self.expressao(item) for item in node["itens"]]
            resultado = self.temporario()
            self.emitir(f"{resultado} = list [{', '.join(itens)}]")
            return resultado
        if tipo == "Indice":
            objeto = self.expressao(node["objeto"])
            indice = self.expressao(node["indice"])
            resultado = self.temporario()
            self.emitir(f"{resultado} = {objeto}[{indice}]")
            return resultado
        if tipo == "Atributo":
            objeto = self.expressao(node["objeto"])
            return f"{objeto}.{node['nome']}"
        raise ValueError(f"Expressão AST não suportada: {tipo}")

    def bloco(self, nodes):
        for node in nodes:
            tipo = node["tipo"]
            if tipo == "Atribuicao":
                valor = self.expressao(node["valor"])
                alvo = node["alvo"]
                if node.get("operador", "=") == "=":
                    self.emitir(f"{alvo} = {valor}")
                else:
                    operador = node["operador"][:-1]
                    self.emitir(f"{alvo} = {alvo} {operador} {valor}")
            elif tipo == "Expressao":
                self.expressao(node["expressao"])
            elif tipo == "Retorno":
                valor = node.get("valor")
                self.emitir("return" if valor is None else f"return {self.expressao(valor)}")
            elif tipo in ("Pass", "Break", "Continue"):
                self.emitir(tipo.lower())
            elif tipo == "Condicional":
                condicao = self.expressao(node["condicao"])
                senao = self.novo_rotulo("L_else")
                fim = self.novo_rotulo("L_fim")
                self.emitir(f"ifFalse {condicao} goto {senao}")
                self.bloco(node["corpo"])
                if node["alternativa"]:
                    self.emitir(f"goto {fim}")
                    self.emitir(f"{senao}:")
                    self.bloco(node["alternativa"])
                    self.emitir(f"{fim}:")
                else:
                    self.emitir(f"{senao}:")
            elif tipo == "Enquanto":
                inicio = self.novo_rotulo("L_inicio")
                fim = self.novo_rotulo("L_fim")
                self.emitir(f"{inicio}:")
                condicao = self.expressao(node["condicao"])
                self.emitir(f"ifFalse {condicao} goto {fim}")
                self.bloco(node["corpo"])
                self.emitir(f"goto {inicio}")
                self.emitir(f"{fim}:")
            elif tipo == "ParaCada":
                iteravel = self.expressao(node["iteravel"])
                iterador = self.temporario()
                inicio = self.novo_rotulo("L_inicio")
                fim = self.novo_rotulo("L_fim")
                self.emitir(f"{iterador} = iter({iteravel})")
                self.emitir(f"{inicio}:")
                proximo = self.temporario()
                self.emitir(f"{proximo} = next({iterador})")
                self.emitir(f"ifEnd {proximo} goto {fim}")
                self.emitir(f"{node['alvo']} = {proximo}")
                self.bloco(node["corpo"])
                self.emitir(f"goto {inicio}")
                self.emitir(f"{fim}:")
            else:
                raise ValueError(f"Comando AST não suportado: {tipo}")

    def gerar(self, ast):
        self.bloco(ast.get("corpo", []))
        return self.linhas


def gerar_codigo_intermediario(ast):
    """Retorna uma representação didática de três endereços."""
    return GeradorCodigoIntermediario().gerar(ast)
