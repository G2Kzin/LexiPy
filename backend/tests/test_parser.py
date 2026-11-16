from parser import parse, ErroSintatico


def test_assignment_and_operator_precedence():
    ast = parse("resultado = 2 + 3 * 4")["ast"]
    expr = ast["corpo"][0]["valor"]
    assert expr["tipo"] == "Binaria"
    assert expr["operador"] == "SOMA"
    assert expr["direita"]["operador"] == "MULTIPLICACAO"


def test_if_else_indented_block():
    ast = parse('idade = 20\nif idade >= 18:\n    print("maior")\nelse:\n    print("menor")')["ast"]
    node = ast["corpo"][1]
    assert node["tipo"] == "Condicional"
    assert len(node["corpo"]) == 1
    assert len(node["alternativa"]) == 1


def test_while_loop():
    ast = parse("while x < 3:\n    x = x + 1")["ast"]
    assert ast["corpo"][0]["tipo"] == "Enquanto"


def test_for_loop():
    ast = parse("for item in lista:\n    print(item)")["ast"]
    assert ast["corpo"][0]["tipo"] == "ParaCada"
    assert ast["corpo"][0]["alvo"] == "item"


def test_function_call_and_list_literal():
    ast = parse("valores = [1, 2, 3]\nprint(valores)")["ast"]
    assert ast["corpo"][0]["valor"]["tipo"] == "Lista"
    assert ast["corpo"][1]["expressao"]["tipo"] == "Chamada"


def test_invalid_expression_reports_syntax_error():
    try:
        parse("x = 1 +")
        assert False, "Era esperado erro sintático."
    except ErroSintatico as exc:
        assert exc.linha == 1
        assert exc.coluna > 0


def test_missing_indented_suite_reports_syntax_error():
    try:
        parse("if x > 1:\nprint(x)")
        assert False, "Era esperado erro sintático."
    except ErroSintatico as exc:
        assert "indentado" in exc.mensagem
