# LexiPy — Etapa 3 integrada (base Etapa 2)

Esta pasta é uma versão integrada: usa os arquivos Docker e a configuração Nginx da Etapa 2 e incorpora o scanner léxico e a interface da Etapa 3. Ela não inclui a pasta `.git`; copie os arquivos para seu repositório existente para preservar o histórico.

## Conteúdo
- `backend/scanner.py`: scanner léxico didático para subconjunto documentado de Python.
- `backend/main.py`: endpoint FastAPI integrado ao scanner, mantendo campos da resposta da Etapa 2.
- `backend/tests/`: testes de API e scanner.
- `frontend/index.html`: interface web com tabela de tokens, contagem e erros.
- `backend/Dockerfile`, `backend/requirements.txt`, `frontend/Dockerfile`, `frontend/nginx.conf`, `docker-compose.yml`: recuperados da Etapa 2.
- `docs/`: escopo e roteiro de testes.

## Aplicar no repositório existente
1. Faça uma cópia de segurança da pasta atual `LexiPy_GitHub`.
2. Copie `backend`, `frontend`, `docs`, `README.md`, `README-ETAPA3.md` e `CHECKLIST-ETAPA3.md` para a raiz de `LexiPy_GitHub`, aceitando substituir arquivos de mesmo nome.
3. Preserve a pasta `.git`, o `.gitignore` e o `docker-compose.yml` da raiz atual. O `docker-compose.yml` desta pasta é recuperado da Etapa 2, mas deve ser comparado antes de substituí-lo.
4. Abra o terminal na raiz de `LexiPy_GitHub` e rode:

```powershell
docker compose up --build -d
docker compose exec backend pytest -v
docker compose ps
```

5. Abra `http://localhost:8080`, teste um exemplo válido e o exemplo com `@`, e confirme a documentação em `http://localhost:8000/docs`.
6. Só após verificar os resultados, rode `git status`, revise as alterações e faça commit.

## Limites
O scanner reconhece um subconjunto didático de Python; não executa código, não valida sintaxe nem cobre toda a linguagem. Os testes incluídos precisam ser executados no seu ambiente.
