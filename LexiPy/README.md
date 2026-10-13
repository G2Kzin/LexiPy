# LexiPy — Jogo educativo de análise léxica

**Trabalho 1 — Estrutura inicial, aplicação web e Docker**  
**Aluno:** Felipe Ferreira Souza  
**Professor:** Bruno Moraes Rocha  
**GitHub do professor:** https://github.com/rocha3runo

## Objetivo
O LexiPy é uma proposta de jogo educativo para apoiar o ensino de análise léxica usando Python. Nesta primeira etapa, a aplicação é apenas um esqueleto funcional: o frontend exibe “Hello, World!” e consulta o backend. As mecânicas do jogo serão implementadas nas próximas etapas.

## Escolhas
- Linguagem-alvo: Python.
- Subconjunto planejado: palavras reservadas, identificadores, literais numéricos e textos simples, operadores, delimitadores, comentários e indentação.
- Etapa: análise léxica.
- Tipo: jogo educativo web.
- Frontend: HTML, CSS, JavaScript e Nginx.
- Backend: Python e Flask.
- Orquestração: Docker Compose.

## Estrutura
```text
LexiPy/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── nginx.conf
│   └── Dockerfile
├── .dockerignore
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Pré-requisitos
Instale Git e Docker Desktop (Windows/macOS) ou Docker Engine (Linux) com Docker Compose v2. Confira:
```bash
git --version
docker --version
docker compose version
```
Não é necessário instalar Python ou Node.js localmente para executar a versão em contêineres.

## Executar
Na pasta que contém `docker-compose.yml`:
```bash
docker compose up --build
```
Abra http://localhost:8080. A página deve mostrar “Hello, World!” e uma mensagem confirmando a resposta do backend.

Endpoints:
- Aplicação: http://localhost:8080
- API: http://localhost:8080/api/hello
- Saúde: http://localhost:8080/api/health

Para executar em segundo plano:
```bash
docker compose up --build -d
```
Logs e estado:
```bash
docker compose logs -f
docker compose ps
```
Encerrar:
```bash
docker compose down
```

## Como funciona
O navegador acessa o frontend na porta 8080. O Nginx entrega os arquivos estáticos e encaminha `/api/` ao serviço Flask pela rede interna do Docker. O Flask responde em JSON. O Compose inicia os dois serviços juntos. Não há banco de dados porque a versão mínima não precisa persistir dados.

## Teste de instalação limpa
Depois de publicar o repositório, clone-o em uma pasta nova e execute os comandos abaixo:
```bash
git clone https://github.com/SEU_USUARIO/LexiPy.git
cd LexiPy
docker compose up --build
```
Acesse http://localhost:8080, verifique a mensagem e a confirmação da API, e finalize com `docker compose down`.

**Importante:** só marque a validação como concluída depois de realmente executar o teste em uma instalação limpa.

## Publicar no GitHub
1. Crie um repositório vazio chamado `LexiPy` em https://github.com/new.
2. Extraia os arquivos desta entrega para a pasta local `LexiPy`.
3. Abra um terminal nessa pasta e execute, substituindo `SEU_USUARIO`:
```bash
git init
git add .
git commit -m "Cria estrutura inicial do LexiPy com Docker"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/LexiPy.git
git push -u origin main
```
Se já houver um `origin`, confira com `git remote -v` antes de adicioná-lo novamente.

## Compartilhar com o professor
O usuário informado é `rocha3runo` (https://github.com/rocha3runo). No repositório, abra **Settings → Collaborators → Add people**, procure `rocha3runo` e envie o convite. Confirme a aceitação conforme as orientações da disciplina. Se o repositório for público, ele poderá visualizar o conteúdo, mas siga a orientação do professor sobre compartilhamento.

## Checklist de entrega
- [ ] Repositório criado e código enviado para `main`.
- [ ] README revisado.
- [ ] Professor convidado ou link compartilhado.
- [ ] `docker compose up --build` executado com sucesso.
- [ ] “Hello, World!” aparece no navegador.
- [ ] Comunicação frontend-backend confirmada.
- [ ] `docker compose down` executado.
- [ ] Teste de instalação limpa realizado e documentado.

## Limites desta etapa
Ainda não há banco de dados, login, pontuação, níveis nem análise real de tokens. O foco é estabelecer uma base reproduzível para as próximas fases.
