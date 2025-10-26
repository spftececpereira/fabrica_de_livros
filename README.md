# Fábrica de Livros

![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-black.svg)

<p align="center">
  <img src="public/placeholder-logo.svg" alt="Fábrica de Livros Logo" width="200"/>
</p>

<h1 align="center">Fábrica de Livros</h1>

<p align="center">
  Uma plataforma web para criar livros de colorir personalizados usando inteligência artificial.
</p>

## ✨ Funcionalidades

- **Autenticação**: Login com Google OAuth via Supabase para uma experiência segura e personalizada.
- **Criação de Livros**: Gere livros de colorir únicos com o poder da IA.
  - **4 Estilos Artísticos**: Escolha entre Cartoon, Mangá, Realista e Clássico.
  - **Tamanho Flexível**: Crie livros com 5 a 20 páginas.
  - **Histórias Educativas**: Adicione narrativas para enriquecer a experiência.
- **Biblioteca Pessoal**: Gerencie todos os seus livros criados em um só lugar.
  - **Busca e Filtros**: Encontre livros por estilo ou status de geração.
  - **Visualização Detalhada**: Acesse e veja os detalhes de cada livro.
- **Gamificação**: Desbloqueie conquistas e badges enquanto cria.
  - **10 Badges**: Colecione todas as conquistas.
  - **Progresso em Tempo Real**: Acompanhe seu desenvolvimento.
- **Exportação em PDF**: Baixe seus livros em alta qualidade para imprimir e colorir.

## 🚀 Tecnologias

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes
- **Banco de Dados**: PostgreSQL (Supabase)
- **Autenticação**: Supabase Auth
- **Storage**: Supabase Storage
- **IA**: Google Gemini
- **Geração de PDF**: jsPDF

## ⚙️ Configuração e Deploy

### 1. Configuração do Supabase

1.  **Crie um projeto no Supabase.**
2.  **Configuração do Banco de Dados**:
    - Navegue até o **SQL Editor** no seu projeto Supabase.
    - Execute os seguintes scripts SQL na ordem apresentada:
      1.  `scripts/001-create-tables.sql`
      2.  `scripts/002-enable-rls.sql`
      3.  `scripts/003-seed-badges.sql`
      4.  `scripts/004-create-user-trigger.sql`
      5.  `scripts/005-sync-existing-users.sql`
      6.  `scripts/006-create-storage-policies.sql`
3.  **Configuração do Storage**:
    - Navegue até a seção **Storage**.
    - Crie um novo bucket com o nome `books-images`.
    - **Importante**: Mantenha o bucket como **privado**. As políticas de segurança (RLS) que você aplicou garantirão o acesso seguro aos arquivos.
4.  **Obtenha suas chaves de API**:
    - Em **Project Settings > API**, copie a `URL` e a `anon key`.

### 2. Configuração Local

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/fabrica-livros.git
    cd fabrica-livros
    ```
2.  **Instale as dependências:**
    ```bash
    npm install
    ```
3.  **Crie o arquivo de variáveis de ambiente**:
    - Renomeie `.env.local.example` para `.env.local`.
    - Adicione as chaves do Supabase e da API do Gemini:
      ```env
      # Supabase
      NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
      NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
      NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL=http://localhost:3000/auth/callback

      # OpenAI
      OPENAI_API_KEY=your_openai_api_key
      ```
4.  **Inicie o servidor de desenvolvimento:**
    ```bash
    npm run dev
    ```

### 3. Deploy com Vercel

1.  **Faça o push do seu código para um repositório Git (GitHub, GitLab, etc.).**
2.  **Importe seu projeto no Vercel.**
3.  **Configure as variáveis de ambiente no painel do Vercel.**
4.  **Clique em "Deploy" e aguarde a mágica acontecer!**

## 📂 Estrutura do Projeto

```
├── app/
│   ├── api/              # API Routes para o backend
│   ├── app/              # Páginas autenticadas da aplicação
│   ├── auth/             # Callbacks de autenticação OAuth
│   ├── login/            # Página de login
│   ├── signup/           # Página de cadastro
│   └── page.tsx          # Landing page pública
├── components/           # Componentes React reutilizáveis
├── lib/
│   ├── ai/               # Lógica para integração com a IA (Gemini)
│   ├── badges/           # Funções para o sistema de gamificação
│   ├── pdf/              # Código para geração de PDF
│   ├── supabase/         # Clientes Supabase (client e server)
│   └── types.ts          # Definições de tipos TypeScript
└── scripts/              # Scripts de migração e seed para o banco de dados
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.