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

## 🛠️ Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) instalados.
- (Opcional) Python 3.12+ e Node.js 20+ para desenvolvimento local fora do Docker.

## 🏁 Como Iniciar (Rápido)

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/fabrica-livros.git
    cd fabrica-livros
    ```

2.  **Configure as Variáveis de Ambiente:**
    Copie o arquivo de exemplo e preencha com sua chave da API do Google Gemini.
    ```bash
    cp .env.example .env
    ```
    Edite o arquivo `.env` e adicione sua `GEMINI_API_KEY`.

3.  **Inicie os Serviços com Docker:**
    ```bash
    docker compose up -d --build
    ```

4.  **Acesse a Aplicação:**
    - **Frontend**: [http://localhost:3000](http://localhost:3000)
    - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
    - **Backend Admin**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📂 Estrutura do Projeto

```
.
├── backend/                # Aplicação FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints (v1)
│   │   ├── core/           # Configurações e Segurança
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Lógica de Negócio (AI, PDF)
│   │   └── worker/         # Tarefas Celery
│   ├── alembic/            # Migrações de Banco de Dados
│   └── requirements.txt    # Dependências Python
├── frontend/               # Aplicação Next.js
│   ├── app/                # App Router (Pages & Layouts)
│   ├── components/         # Componentes React (UI)
│   ├── lib/                # Utilitários (API Client)
│   └── package.json        # Dependências Node.js
├── docker-compose.yml      # Orquestração dos serviços
└── .env.example            # Exemplo de variáveis de ambiente
```

## 🔧 Desenvolvimento Local

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
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