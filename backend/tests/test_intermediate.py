from intermediate import gerar_codigo_intermediario


def test_assignment_and_expression_generate_three_address_code():
    ast = {
        "tipo": "Programa",
        "corpo": [{
            "tipo": "Atribuicao",
            "alvo": "resultado",
            "operador": "=",
            "valor": {
                "tipo": "Binaria",
                "operador": "SOMA",
                "esquerda": {"tipo": "Numero", "valor": "10"},
                "direita": {"tipo": "Numero", "valor": "5"},
            },
        }],
    }
    assert gerar_codigo_intermediario(ast) == [
        "t1 = 10 + 5",
        "resultado = t1",
    ]


def test_if_generates_conditional_labels():
    ast = {
        "tipo": "Programa",
        "corpo": [{
            "tipo": "Condicional",
            "condicao": {"tipo": "Literal", "valor": "True"},
            "corpo": [{"tipo": "Pass"}],
            "alternativa": [],
        }],
    }
    codigo = gerar_codigo_intermediario(ast)
    assert codigo[0] == "ifFalse True goto L_else1"
    assert "pass" in codigo
    assert codigo[-1] == "L_else1:"
