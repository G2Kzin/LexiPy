# LexiPy — Etapa 4 (análise léxica e sintática)

Projeto educacional para demonstrar etapas iniciais de um compilador usando um subconjunto didático de Python.

## Funcionalidades
- Interface web para inserir ou selecionar código de exemplo.
- API FastAPI com análise léxica pelo scanner da Etapa 3.
- Análise sintática por parser recursivo descendente.
- Construção de AST em estrutura JSON.
- Diagnósticos sintáticos com linha e coluna.
- Separação entre erros léxicos e sintáticos.
- Execução local com Docker Compose e testes automatizados com pytest.

## Escopo sintático desta etapa
A gramática implementada é intencionalmente parcial. Inclui atribuições simples e compostas, expressões com precedência de operadores, chamadas de função, listas, indexação, acesso a atributo, comandos `if/else`, `while`, `for/in`, `return`, `pass`, `break` e `continue`. Não é um parser completo de Python. Funções/classes, importações, exceções, compreensão de listas, tuplas e várias construções da linguagem completa permanecem fora do escopo.

A AST é uma estrutura de dicionários serializável em JSON. O analisador não executa o código e não realiza análise semântica ou geração de código.

## Estrutura
- `backend/scanner.py`: análise léxica da Etapa 3.
- `backend/parser.py`: parser e construção da AST.
- `backend/main.py`: endpoints e integração das duas fases.
- `backend/tests/test_parser.py`: testes unitários do parser.
- `backend/tests/test_api.py`: testes de integração da API.
- `frontend/index.html`: interface para tokens, erros sintáticos e AST.
- `docker-compose.yml`: orquestração da aplicação.
- `docs/gramatica-sintatica.md`: gramática e limitações.\n- `docs/materiais-metodos-etapa4.md`: procedimento, fluxo e critérios de avaliação.
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
`POST /api/analisar` recebe `{"codigo":"x = 10\\nprint(x)"}`. A resposta mantém os campos léxicos (`sucesso`, `tokens`, `erros`) e acrescenta:
- `sintaxe_sucesso`: `true`, `false` ou `null` quando a análise sintática não pôde ser executada por erro léxico.
- `ast`: árvore sintática quando a análise for válida; caso contrário, `null`.
- `erros_sintaticos`: lista de diagnósticos sintáticos com tipo, mensagem, linha e coluna.
- `status`: `success`, `lexical_errors` ou `syntax_errors`.

## Validação
Os testes foram adicionados ao repositório, mas precisam ser executados no ambiente do projeto antes de declarar a etapa validada. Não confundir existência de testes com aprovação dos testes.
