# Registro de testes — Etapa 3

## Comandos para validação

Execute na raiz do repositório:

```bash
docker compose up --build -d
docker compose exec backend pytest -v
docker compose ps
docker compose down
```

Validação manual recomendada:
1. Abrir `http://localhost:8080`.
2. Selecionar um exemplo e alterar o código.
3. Analisar um programa válido e conferir tipo, lexema, linha e coluna.
4. Analisar o exemplo com `@` e confirmar a mensagem de erro.
5. Testar entrada vazia e confirmar a mensagem na interface.
6. Confirmar que a API continua respondendo em `http://localhost:8000/docs`.

## Cobertura incluída no pacote

- Testes unitários: palavras reservadas, identificadores, literais inteiros/reais/strings, operadores, delimitadores, comentários, espaços, posições, caracteres inválidos, strings não terminadas e strings triplas fora do escopo.
- Testes de API: health check, endpoint legado, tokens, erros léxicos, entrada vazia, campo ausente e posições.

## Resultado desta entrega

Os testes estão escritos no pacote. **Ainda precisam ser executados no ambiente local do aluno** para registrar o resultado real. Não declarar “todos passaram” antes de executar os comandos acima no Docker Compose.

| Verificação | Status |
|---|---|
| Testes unitários do scanner | Pendente de execução local |
| Testes do endpoint | Pendente de execução local |
| Docker Compose após substituição | Pendente de execução local |
| Interface em navegador | Pendente de verificação manual |
| Regressão da Etapa 2 | Pendente de execução local |

## Observação de compatibilidade

O endpoint mantém os campos `mensagem`, `recebido`, `caracteres`, `linhas` e `status` usados na Etapa 2, acrescentando `sucesso`, `tokens` e `erros`.
