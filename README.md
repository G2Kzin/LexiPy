# LexiPy — Etapa 4 (análise léxica e sintática)

Projeto educacional para demonstrar etapas iniciais de um compilador usando um subconjunto didático de Python.

## Funcionalidades

- Interface web para inserir ou selecionar código de exemplo.
- API FastAPI com análise léxica pelo scanner da Etapa 3.
- Análise sintática por parser recursivo descendente.
- Construção de AST em estrutura JSON com posição de origem.
- Diagnósticos sintáticos com linha e coluna.
- Separação entre erros léxicos e sintáticos.
- Execução local com Docker Compose e testes automatizados com pytest.

## Escopo sintático

A gramática é parcial e está documentada em `docs/gramatica-sintatica.md`. Inclui atribuições simples e compostas, expressões com precedência de operadores, chamadas de função, listas, indexação, acesso a atributo, comandos `if/else`, `while`, `for/in`, `return`, `pass`, `break` e `continue`. Não é um parser completo de Python. Funções/classes, importações, exceções, compreensão de listas, tuplas e outras construções permanecem fora do escopo.

O scanner da Etapa 3 continua responsável pelos tokens apresentados ao usuário. Como ele não emite tokens estruturais de quebra de linha e indentação, o parser recebe o texto-fonte e usa internamente o `tokenize` da biblioteca padrão para obter esses limites. O parser só é executado quando não há erros léxicos. A AST é serializável em JSON. O sistema não executa o código e não realiza análise semântica ou geração de código.

## Estrutura

- `backend/scanner.py`: análise léxica da Etapa 3.
- `backend/parser.py`: parser e construção da AST.
- `backend/main.py`: endpoints e integração das duas fases.
- `backend/tests/test_parser.py`: testes unitários do parser.
- `backend/tests/test_api.py`: testes de integração da API.
- `frontend/index.html`: interface para tokens, erros sintáticos e AST.
- `docker-compose.yml`: orquestração da aplicação.
- `docs/gramatica-sintatica.md`: gramática, precedência e limitações.
- `docs/materiais-metodos-etapa4.md`: procedimento, fluxo e critérios de avaliação.
- `docs/escopo-lexico.md`: escopo do scanner.

## Executar

Na raiz do repositório:

```bash
docker compose up --build -d
docker compose exec backend pytest -v
docker compose ps
```

Interface: http://localhost:8080  
Documentação da API: http://localhost:8000/docs

## Contrato da API

`POST /api/analisar` recebe, por exemplo, `{"codigo":"x = 10\\nprint(x)"}`. A resposta mantém os campos da análise léxica (`sucesso`, `tokens`, `erros`) e acrescenta:

- `sintaxe_sucesso`: `true`, `false` ou `null` quando a análise sintática não é executada por erro léxico.
- `ast`: árvore sintática quando a análise é válida; caso contrário, `null`.
- `erros_sintaticos`: lista de diagnósticos com tipo, mensagem, linha e coluna.
- `status`: `success`, `lexical_errors` ou `syntax_errors`.

Código vazio é rejeitado com HTTP 422. Erros sintáticos são retornados como resultado da análise (HTTP 200), separados dos erros léxicos.

## Testes e validação

A integração contínua do GitHub Actions executa os testes Python e uma validação Docker Compose. Na execução de validação registrada para a Etapa 4, os dois jobs concluíram com sucesso: testes Python e validação Docker. O job Docker validou a configuração, construiu e iniciou os serviços, aguardou o healthcheck, testou a página e o endpoint integrado por HTTP e executou novamente os testes dentro do container.

Execução validada: [GitHub Actions — Testes do LexiPy](https://github.com/G2Kzin/LexiPy/actions/runs/43974916553).

Para repetir localmente, execute os comandos da seção anterior. A verificação automatizada da interface foi feita por requisições HTTP; não se afirma que houve teste manual em navegador.
