# Gramática sintática do LexiPy — Etapa 4

## Estratégia
Parser recursivo descendente com precedência de operadores (precedence climbing). O módulo usa o tokenizer da biblioteca padrão do Python para preservar quebras de linha e níveis de indentação, enquanto o scanner próprio da Etapa 3 permanece responsável pela análise léxica apresentada ao usuário. O parser só é chamado quando o scanner não relata erro léxico.

## Gramática simplificada (EBNF)

```ebnf
programa       = { comando } ;
comando        = atribuicao | expressao_comando | condicional
               | laco_while | laco_for | comando_controle ;
condicional    = "if", expressao, suite, [ "else", suite ] ;
laco_while     = "while", expressao, suite ;
laco_for       = "for", IDENTIFICADOR, "in", expressao, suite ;
suite          = ":", comando_simples
               | ":", NOVA_LINHA, INDENT, { comando }, DEDENT ;
atribuicao     = IDENTIFICADOR, operador_atribuicao, expressao ;
expressao      = expressao_logica ;
expressao_logica = expressao_comparacao, { ("and" | "or"), expressao_comparacao } ;
expressao_comparacao = expressao_aritmetica,
                       { operador_comparacao, expressao_aritmetica } ;
expressao_aritmetica = termo, { ("+" | "-"), termo } ;
termo          = fator, { ("*" | "/" | "//" | "%"), fator } ;
fator          = operador_unario, fator | primario ;
primario       = NUMERO | STRING | BOOLEANO | IDENTIFICADOR
               | chamada | lista | "(", expressao, ")" ;
chamada        = IDENTIFICADOR, "(", [ expressao, { ",", expressao } ], ")" ;
lista          = "[", [ expressao, { ",", expressao } ], "]" ;
comando_controle = "pass" | "break" | "continue" | "return", [ expressao ] ;
```

A implementação também reconhece potência, indexação, acesso a atributo e atribuições compostas. A gramática acima é uma visão didática resumida, não uma especificação completa de Python.

## Árvore sintática abstrata
A AST é composta por objetos JSON com campo `tipo`. Exemplos de nós: `Programa`, `Atribuicao`, `Binaria`, `Unaria`, `Condicional`, `Enquanto`, `ParaCada`, `Chamada`, `Lista`, `Numero`, `Texto` e `Identificador`.

## Limitações conhecidas
- Não implementa toda a gramática Python.
- Não implementa declarações `def` ou `class`, importações e tratamento de exceções.
- Não faz análise semântica, verificação de tipos ou execução.
- Diagnóstico interrompe a análise no primeiro erro sintático (sem recuperação de múltiplos erros).
- O tokenizer da biblioteca padrão é usado internamente para obter indentação; ele não substitui o scanner didático exibido na interface.
