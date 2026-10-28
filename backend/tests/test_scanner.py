from scanner import scan

def token_pairs(result):
    return [(t["tipo"], t["lexema"]) for t in result["tokens"]]

def test_keywords_identifiers_and_assignment():
    result = scan("if numero == 10:\n    print(numero)")
    assert result["sucesso"] is True
    pairs = token_pairs(result)
    assert ("PALAVRA_RESERVADA", "if") in pairs
    assert ("IDENTIFICADOR", "numero") in pairs
    assert ("OPERADOR_RELACIONAL", "==") in pairs
    assert ("LITERAL_INTEIRO", "10") in pairs

def test_string_and_float_literals():
    result = scan('nome = "Ana"\nnota = 8.5')
    assert ("LITERAL_STRING", '"Ana"') in token_pairs(result)
    assert ("LITERAL_REAL", "8.5") in token_pairs(result)

def test_comments_and_whitespace_are_ignored():
    result = scan("x = 2  # comentário\n\n# outro comentário\nprint(x)")
    assert result["sucesso"] is True
    assert all("#" not in t["lexema"] for t in result["tokens"])
    assert not any(t["tipo"] == "ESPACO" for t in result["tokens"])

def test_delimiters_and_compound_operators():
    result = scan("lista[0] >= 2 and lista != []")
    pairs = token_pairs(result)
    assert ("DELIMITADOR", "[") in pairs
    assert ("OPERADOR_RELACIONAL", ">=") in pairs
    assert ("OPERADOR_LOGICO", "and") in pairs
    assert ("OPERADOR_RELACIONAL", "!=") in pairs

def test_line_and_column_are_recorded():
    result = scan("x = 1\n  y = 2")
    y = next(t for t in result["tokens"] if t["lexema"] == "y")
    assert (y["linha"], y["coluna"]) == (2, 3)

def test_unknown_characters_accumulate_errors_and_continue():
    result = scan("x = @\ny = $")
    assert result["sucesso"] is False
    assert [e["lexema"] for e in result["erros"]] == ["@", "$"]
    assert any(t["lexema"] == "y" for t in result["tokens"])

def test_unclosed_string_is_reported():
    result = scan('nome = "Ana')
    assert result["sucesso"] is False
    assert result["erros"][0]["tipo"] == "ERRO_LEXICO"
    assert "não terminada" in result["erros"][0]["mensagem"]

def test_triple_quoted_string_is_out_of_scope():
    result = scan('texto = """abc"""')
    assert result["sucesso"] is False
    assert any("aspas triplas" in e["mensagem"] for e in result["erros"])

def test_empty_scanner_input_is_safe():
    result = scan("")
    assert result == {"sucesso": True, "tokens": [], "erros": []}
