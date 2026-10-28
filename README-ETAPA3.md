# LexiPy — instruções de integração da Etapa 3

Este pacote contém uma implementação da análise léxica para o LexiPy, mantendo o backend FastAPI e a interface web servida pelo Nginx.

## Arquivos incluídos

- `backend/scanner.py`: scanner, categorias de tokens e acumulação de erros.
- `backend/main.py`: endpoint `/api/analisar` integrado ao scanner e compatível com campos antigos da Etapa 2.
- `backend/tests/test_scanner.py`: testes unitários.
- `backend/tests/test_api.py`: testes do contrato HTTP.
- `frontend/index.html`: interface para entrada de código, tabela de tokens, contadores por categoria e mensagens de erro.
- `docs/escopo-lexico.md`: escopo e contrato da API.
- `docs/registro-testes-etapa3.md`: roteiro para registrar a execução real.

## Como aplicar

1. Faça uma cópia de segurança ou crie uma branch:
   ```bash
   git checkout -b feat/etapa3-analisador-lexico
   ```
2. Copie os arquivos deste pacote para os caminhos correspondentes na raiz do repositório `LexiPy`, substituindo os arquivos de mesmo nome.
3. Preserve os arquivos existentes `docker-compose.yml`, `backend/Dockerfile`, `backend/requirements.txt`, `frontend/Dockerfile` e `frontend/nginx.conf`, a menos que o seu ambiente indique um problema específico.
4. Confirme que `backend/requirements.txt` contém `fastapi`, `uvicorn`, `pydantic` e `pytest` (e a versão de `httpx` compatível com o `TestClient`, se usada).
5. Execute:
   ```bash
   docker compose up --build -d
   docker compose exec backend pytest -v
   ```
6. Abra `http://localhost:8080`, teste um exemplo válido e o exemplo com erro.
7. Atualize o README principal com o escopo e o contrato descritos em `docs/escopo-lexico.md`.
8. Só depois das verificações, registre o resultado real em `docs/registro-testes-etapa3.md` e faça commit:
   ```bash
   git add backend frontend docs README.md
   git commit -m "feat: implementa scanner léxico e exibição de tokens"
   git push origin main
   ```

## Atenção

O pacote foi preparado com base na estrutura pública atual do repositório e na especificação da Tarefa 3. O ambiente Docker do seu computador não foi executado por esta entrega; valide os testes e a interface localmente antes de afirmar que tudo passou. O scanner reconhece um subconjunto explícito de Python, não toda a especificação da linguagem.
