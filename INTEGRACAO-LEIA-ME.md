# Como integrar com segurança

O arquivo ZIP não contém `.git`. Ele é um pacote de arquivos para copiar sobre o repositório existente.

**Antes de copiar:** confirme que a raiz é `LexiPy_GitHub` e faça backup.

Copie estas entradas para `LexiPy_GitHub`: `backend/`, `frontend/`, `docs/`, `README.md`, `README-ETAPA3.md`, `CHECKLIST-ETAPA3.md`. Preserve `.git/` e `.gitignore`. O `docker-compose.yml` da Parte 2 foi incluído no pacote como referência; como seu atual compose já aponta para `./backend` e `./frontend`, não o substitua sem necessidade.

Os Dockerfiles e o `nginx.conf` foram recuperados da Parte 2.
