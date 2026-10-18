# LexiPy — Trabalho 2

O **LexiPy** é uma aplicação web educacional para apoiar o aprendizado de análise léxica usando pequenos programas em Python. Nesta etapa, o objetivo é permitir que a pessoa usuária selecione ou escreva um trecho de código, envie-o ao backend e visualize a resposta da API.

> **Escopo desta versão:** o sistema recebe e valida o código enviado, mas ainda não executa o programa Python nem classifica tokens. A implementação do analisador léxico será realizada em uma etapa posterior.

## Funcionalidades

- Interface web responsiva com editor de código-fonte Python.
- Seletor de exemplos que podem ser carregados e editados.
- Envio do código para a API por meio do botão de análise.
- Exibição da resposta retornada pelo servidor.
- Validação de entradas vazias ou compostas somente por espaços.
- Mensagens para falhas de comunicação com o backend.
- Endpoint de saúde para verificar a disponibilidade da API.

## Tecnologias

- **Frontend:** HTML, CSS e JavaScript, servido por Nginx.
- **Backend:** Python, FastAPI e Pydantic.
- **Ambiente:** Docker Compose.
- **Testes:** pytest e FastAPI TestClient.

## Como executar com Docker Compose

Abra o terminal na pasta que contém o arquivo `docker-compose.yml` e execute:

```bash
docker compose up --build
```

Quando os serviços iniciarem, abra a aplicação no navegador:

- Frontend: http://localhost:8080
- Documentação interativa da API: http://localhost:8000/docs

Para encerrar os serviços, pressione `Ctrl+C` no terminal em que o Compose está rodando ou execute em outro terminal, na mesma pasta:

```bash
docker compose down
```

## Exemplos disponíveis

1. **Saída de texto:** `print("Olá, mundo!")` — chamada de função e texto entre aspas.
2. **Variáveis e números:** atribuição de valores e chamada de `print`.
3. **Condicional:** estrutura `if/else`, comparação e indentação.

Os exemplos podem ser selecionados na interface e alterados antes de serem enviados.

## API

### `GET /api/health`

Retorna o estado de saúde do backend. O resultado esperado quando a API está disponível é semelhante a:

```json
{"status":"healthy"}
```

### `GET /api/hello`

Endpoint inicial mantido para verificar a comunicação básica com o backend.

### `POST /api/analisar`

Recebe um objeto JSON com o código-fonte no campo `codigo`. Exemplo de requisição:

```json
{"codigo":"print('Olá')"}
```

A resposta confirma o recebimento e informa metadados básicos do texto, como quantidade de caracteres e linhas. **Essa resposta não representa uma análise léxica:** a classificação de tokens ainda não faz parte desta versão.

Código vazio ou composto apenas por espaços é rejeitado com HTTP `422`. Campos ausentes ou com tipos inválidos também são validados pelo FastAPI/Pydantic.

## Testes automatizados

Os testes podem ser executados dentro do contêiner do backend, com os serviços iniciados, usando um segundo terminal aberto na pasta do `docker-compose.yml`:

```bash
docker compose exec backend pytest -v
```

Também é possível executar os testes localmente, a partir da pasta `backend`, depois de instalar as dependências:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

Os testes cobrem o health check, o endpoint inicial, o envio de código, entradas vazias, espaços em branco, campo ausente e caracteres especiais.

### Resultado verificado durante o desenvolvimento

Em 18 de outubro de 2026, a execução de `docker compose exec backend pytest -v` apresentou **7 testes aprovados** (`7 passed`). Foi exibido também um aviso de depreciação de uma dependência (`DeprecationWarning`), sem impedir a aprovação dos testes.

## Limitações conhecidas

- O código enviado não é executado pelo sistema.
- A análise léxica, sintática e semântica ainda não foi implementada.
- Os testes automatizados desta versão cobrem o backend/API; não foram incluídos testes automatizados de navegador (end-to-end).
- O resultado de execução pode variar conforme o ambiente e as dependências instaladas.

## Histórico de desenvolvimento

Sugestão de mensagem de commit:

```text
feat: add Python editor, examples, API validation and tests for task 2
```
