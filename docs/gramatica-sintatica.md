# Gramática sintática do LexiPy — Etapa 4

## Estratégia e integração

O parser é descendente recursivo, com análise de expressões por precedência (precedence climbing). O scanner didático da Etapa 3 continua identificando os lexemas, categorias e posições exibidos na interface. Quando não há erro léxico, o parser recebe o texto-fonte e usa o módulo `tokenize` da biblioteca padrão do Python para obter também `NEWLINE`, `INDENT` e `DEDENT`, que o scanner da Etapa 3 não produz. Portanto, o parser não consome diretamente a lista de tokens do scanner: essa decisão preserva o scanner existente e permite reconhecer blocos indentados. A limitação fica explícita para não confundir as duas etapas.

## Terminais e correspondência com o scanner

- `IDENTIFICADOR`: categoria de identificador do scanner; o parser também reconhece nomes reservados usados como comandos.
- `NUMERO`: categoria numérica do scanner.
- `STRING`: categoria de cadeia de caracteres do scanner.
- `OPERADOR`: operadores aritméticos, relacionais, lógicos e de atribuição reconhecidos pelo scanner.
- `DELIMITADOR`: parênteses, colchetes, vírgula, ponto e dois-pontos reconhecidos pelo scanner.
- `NOVA_LINHA`, `INDENT`, `DEDENT`, `EOF`: limites estruturais obtidos pelo `tokenize` da biblioteca padrão, não emitidos pelo scanner da Etapa 3.
- Palavras-chave `if`, `else`, `while`, `for`, `in`, `is`, `and`, `or`, `not`, `return`, `pass`, `break` e `continue`: reconhecidas pelo texto do lexema.

## Gramática EBNF

A gramática abaixo descreve o subconjunto implementado. `NOME`, `NUMERO` e `STRING` representam tokens, e `EOF` representa o fim da entrada.

```ebnf
programa       = { comando }, EOF ;

comando        = condicional | laco_while | laco_for | comando_simples ;

condicional    = "if", expressao, suite, [ "else", suite ] ;
laco_while     = "while", expressao, suite ;
laco_for       = "for", NOME, "in", expressao, suite ;

suite          = ":", comando_simples
               | ":", NOVA_LINHA, INDENT, { comando }, DEDENT ;

comando_simples = "pass" | "break" | "continue"
                | "return", [ expressao ]
                | expressao, [ operador_atribuicao, expressao ] ;

operador_atribuicao = "=" | "+=" | "-=" | "*=" | "/=" | "//=" | "%=" | "**=" ;

expressao      = expressao_or ;
expressao_or   = expressao_and, { "or", expressao_and } ;
expressao_and  = expressao_comparacao, { "and", expressao_comparacao } ;
expressao_comparacao = expressao_soma,
                       { ("==" | "!=" | "<" | "<=" | ">" | ">=" | "in" | "is"), expressao_soma } ;
expressao_soma = termo, { ("+" | "-"), termo } ;
termo          = fator, { ("*" | "/" | "//" | "%"), fator } ;
fator          = ("+" | "-" | "not"), fator | potencia ;
potencia       = posfixa, [ "**", fator ] ;
posfixa        = primario, { chamada | indice | atributo } ;
chamada        = "(", [ expressao, { ",", expressao } ], ")" ;
indice         = "[", expressao, "]" ;
atributo       = ".", NOME ;

primario       = NUMERO | STRING | "True" | "False" | "None"
               | NOME | "(", expressao, ")" | lista ;
lista          = "[", [ expressao, { ",", expressao } ], "]" ;
```

A produção de atribuição é restringida na implementação: o lado esquerdo deve ser um identificador simples. Chamadas, índices e atributos são aceitos como expressões, mas não como alvos de atribuição. A implementação aceita chamadas/indexação/acesso a atributo após identificadores; a EBNF acima é uma descrição didática resumida desses sufixos.

## Precedência e associatividade

Da menor para a maior precedência: `or`, `and`, comparações (`== != < <= > >= in is`), soma/subtração, multiplicação/divisão/divisão inteira/resto, sinais unários, potência e expressões primárias/pós-fixas. Os operadores binários, exceto potência, associam à esquerda; potência associa à direita. O operador `not` é tratado como unário com limite de precedência de comparação, conforme o código do parser.

## AST

A resposta contém uma árvore JSON. Cada nó possui `tipo`, `linha` e `coluna`, além dos atributos específicos. Tipos implementados incluem `Programa`, `Atribuicao`, `Expressao`, `Binaria`, `Unaria`, `Condicional`, `Enquanto`, `ParaCada`, `Chamada`, `Indice`, `Atributo`, `Lista`, `Numero`, `Texto`, `Literal`, `Identificador` e nós de controle (`Pass`, `Break`, `Continue`, `Retorno`).

Tokens são unidades léxicas; a árvore de derivação representa aplicações das produções gramaticais; a AST elimina detalhes sintáticos auxiliares e mantém a estrutura relevante do programa. O LexiPy apresenta tokens e AST separadamente.

## Exemplos

Válido:
```python
total = 2 + 3 * 4
if total >= 10:
    print(total)
else:
    print(0)
```

Inválido (operando ausente):
```python
total = 2 +
```

Inválido (bloco sem indentação):
```python
if total > 1:
print(total)
```

## Erros e limites

O parser informa o primeiro erro sintático encontrado, com mensagem, linha e coluna; não há recuperação para continuar a análise e listar vários erros. A API não chama o parser quando o scanner acusa erro léxico. O subconjunto não inclui declarações `def`/`class`, importações, exceções, compreensão de listas, tuplas, lambdas, f-strings ou toda a sintaxe de Python. Não executa o programa, não faz análise semântica, verificação de tipos ou geração de código.
