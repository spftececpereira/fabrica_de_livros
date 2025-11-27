# Fábrica de Livros v2 📚✨

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)

**Fábrica de Livros** é uma plataforma web moderna para criar livros infantis personalizados usando Inteligência Artificial. A versão 2 (v2) foi reescrita com uma arquitetura robusta e escalável, separando o backend e frontend em serviços distintos orquestrados via Docker.

## 🚀 Arquitetura

O projeto segue uma arquitetura de microsserviços simplificada (Monorepo):

- **Backend**: Python 3.12 + FastAPI (Async).
  - **Banco de Dados**: PostgreSQL (Async SQLAlchemy).
  - **Filas**: Celery + Redis (para geração assíncrona de livros).
  - **IA**: Abstração para múltiplos provedores (Google Gemini implementado).
  - **Auth**: JWT + OAuth2.
- **Frontend**: Next.js 15 (App Router) + React 19 + Tailwind CSS 4.
- **Infraestrutura**: Docker Compose para orquestração local.

## ✨ Funcionalidades

- **Autenticação Segura**: Login e Registro com JWT.
- **Geração de Livros com IA**:
  - Criação de histórias baseadas em Título, Tema e Estilo.
  - Processamento assíncrono (background workers).
- **Leitor de Livros**: Interface imersiva para leitura das histórias geradas.
- **Exportação PDF**: Download dos livros gerados em formato PDF pronto para impressão.
- **Dashboard**: Gerenciamento da biblioteca pessoal de livros.

## ⚙️ Configuração e Variáveis de Ambiente

O projeto utiliza variáveis de ambiente para configuração. Você deve criar um arquivo `.env` na pasta `backend/` (para desenvolvimento local sem Docker) ou configurar as variáveis no `docker-compose.yml` (já pré-configurado para dev).

### Variáveis Obrigatórias (Backend)

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `DATABASE_URL` | Connection string do PostgreSQL (Async) | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | URL de conexão do Redis | `redis://host:6379/0` |
| `SECRET_KEY` | Chave secreta para assinatura de tokens JWT | `sua_chave_super_secreta` |
| `GEMINI_API_KEY` | Chave da API do Google Gemini (para geração de livros) | `AIzaSy...` |

### Variáveis Opcionais

| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `ALGORITHM` | Algoritmo de criptografia do JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token (minutos) | `30` |

## 🐳 Desenvolvimento com Docker (Recomendado)

A maneira mais fácil de rodar o projeto é usando Docker Compose, pois ele sobe automaticamente o Banco de Dados, Redis, Backend, Frontend e Worker.

1.  **Configure a API Key da IA:**
    Crie um arquivo `.env` na raiz do projeto (ou edite o `docker-compose.yml` diretamente se preferir, mas não commite segredos):
    ```bash
    cp .env.example .env
    ```
    Edite o `.env` e adicione sua `GEMINI_API_KEY`.

2.  **Inicie os serviços:**
    ```bash
    docker compose up -d --build
    ```
    Isso irá construir as imagens e iniciar os containers:
    - `backend`: http://localhost:8000
    - `frontend`: http://localhost:3000
    - `db`: PostgreSQL (porta 5432)
    - `redis`: Redis (porta 6379)
    - `worker`: Processamento de tarefas em segundo plano (Celery)

3.  **Logs:**
    Para ver os logs de todos os serviços:
    ```bash
    docker compose logs -f
    ```

## 🔧 Desenvolvimento Local (Híbrido)

Se você deseja rodar o **Backend** ou **Frontend** fora do Docker (para debugar ou desenvolver mais rápido), você **PRECISA** ter os serviços de infraestrutura (Postgres e Redis) rodando.

1.  **Suba apenas a infraestrutura:**
    ```bash
    docker compose up -d db redis
    ```

2.  **Backend Local:**
    - Crie o arquivo `backend/.env` com as configurações apontando para `localhost`:
      ```env
      DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fabrica_livros
      REDIS_URL=redis://localhost:6379/0
      SECRET_KEY=dev_secret
      GEMINI_API_KEY=sua_chave
      ```
    - Instale as dependências e rode:
      ```bash
      cd backend
      python -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
      uvicorn app.main:app --reload
      ```

3.  **Frontend Local:**
    - Certifique-se que o backend está rodando.
    - Instale e rode:
      ```bash
      cd frontend
      pnpm install
      pnpm dev
      ```


## 🧪 Testes

O backend possui testes configurados (a ser expandido).
```bash
docker compose exec backend pytest
```

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.



As seguintes pastas vazias precisam ser removidas manualmente (não posso deletar diretórios vazios):                 │
│                                                                                                                      │
│  • frontend/app/api/badges/all                                                                                       │
│  • frontend/app/api/books/[id]/pdf                                                                                   │
│  • frontend/app/auth/callback                                                                                        │
│  • frontend/app/login, frontend/app/register, frontend/app/signup                                                    │
│  • frontend/lib/hooks, frontend/lib/supabase                                                                         │
