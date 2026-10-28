# LexiPy — Escopo léxico (Etapa 3)

## Objetivo e limites

O LexiPy reconhece tokens de um subconjunto didático de Python. O scanner não executa o programa e não valida a gramática, a indentação como estrutura sintática, tipos ou significado. A análise sintática fica para a Etapa 4.

## Categorias suportadas

| Categoria | Exemplos / regra |
|---|---|
| Palavras reservadas | Palavras da lista de palavras-chave do Python disponível na versão do interpretador, como `if`, `else`, `for`, `while`, `def`, `return`, `class`, `import`, `try`, `except`, `pass`, `break` |
| Identificadores | ASCII: letra ou `_` inicial, seguida por letras ASCII, dígitos ou `_`; exemplos `nome`, `_x1`, `resultado2` |
| Literais inteiros | Sequências de dígitos ASCII, como `0`, `10`, `2048` |
| Literais reais | Números decimais com ponto e dígitos dos dois lados, como `3.14`, `0.5` |
| Literais string | Texto entre aspas simples ou duplas na mesma linha, por exemplo `'oi'`, `"Olá"`; escapes com barra invertida são percorridos |
| Literais booleanos/nulos | `True`, `False`, `None` |
| Operadores aritméticos | `+`, `-`, `*`, `/`, `//`, `%`, `**` |
| Operadores de atribuição | `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `**=`, `//=` |
| Operadores relacionais | `==`, `!=`, `<`, `>`, `<=`, `>=`, palavras `in` e `is` |
| Operadores lógicos | `and`, `or`, `not` |
| Outros operadores | `->` é reconhecido como `OPERADOR` |
| Delimitadores | `(`, `)`, `[`, `]`, `{`, `}`, `:`, `,`, `.`, `;` |
| Comentários | Comentários iniciados por `#` até o fim da linha são ignorados |
| Espaços em branco | Espaços, tabulações, retornos de carro e quebras de linha são ignorados como tokens; linha/coluna são atualizadas |

## Fora do escopo / erros

- Caractere não reconhecido gera erro com lexema, linha e coluna, e o scanner continua.
- String sem fechamento na mesma linha gera erro léxico.
- Strings triplas são explicitamente não suportadas e geram erro.
- Identificadores Unicode, literais numéricos com expoente, bases hexadecimais/binárias, prefixos de string (`f`, `r`, `b`, `u`), strings multilinha e escapes de continuação de linha não são parte do subconjunto garantido.
- O scanner pode tokenizar trechos que depois serão rejeitados sintaticamente. Isso é esperado nesta etapa.

## Contrato HTTP

### Requisição

`POST /api/analisar`

```json
{"codigo": "x = 10\nprint(x)"}
```

### Resposta sem erro léxico

```json
{
  "sucesso": true,
  "tokens": [
    {"tipo": "IDENTIFICADOR", "lexema": "x", "linha": 1, "coluna": 1},
    {"tipo": "OPERADOR_ATRIBUICAO", "lexema": "=", "linha": 1, "coluna": 3},
    {"tipo": "LITERAL_INTEIRO", "lexema": "10", "linha": 1, "coluna": 5}
  ],
  "erros": [],
  "mensagem": "Análise léxica concluída.",
  "recebido": true,
  "caracteres": 16,
  "linhas": 2,
  "status": "success"
}
```

A lista acima é ilustrativa; os campos `caracteres` e `linhas` dependem exatamente do texto enviado.

### Resposta com erro léxico

A API responde HTTP 200 quando a requisição foi processada, mesmo que o scanner encontre erros. Nesse caso, `sucesso` é `false`, `erros` contém as ocorrências e `status` é `lexical_errors`. Entrada vazia/composta apenas por espaços continua retornando HTTP 422.

## Exemplo de erro

Para `valor = @`, o erro inclui `lexema: "@"`, linha 1, coluna 9 e mensagem orientando o usuário sobre o caractere não reconhecido.

## Como executar

Na raiz do projeto:

```bash
docker compose up --build
```

Acesse `http://localhost:8080` e `http://localhost:8000/docs`.

Para executar os testes:

```bash
docker compose exec backend pytest -v
```

## Limitações conhecidas

O scanner é intencionalmente didático, não é uma implementação completa da especificação léxica do Python. Não executa código, não produz tokens de indentação/newline e não faz parsing. A interface mostra a tabela de tokens e erros, mas ainda não faz realce por cor do código-fonte nem animação passo a passo.
