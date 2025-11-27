# Frontend - Fábrica de Livros v2

## 🚀 Arquitetura Implementada

### ✅ **Sistema de Autenticação Completo**
- **JWT Tokens** conectados diretamente ao backend FastAPI
- **AuthProvider** moderno com TanStack Query + Zustand
- **Middleware** de proteção de rotas automático
- **Refresh automático** de tokens
- **Sistema de permissões** robusto (user/premium/admin)

### ✅ **Gerenciamento de Estado Moderno**
- **Zustand** para estado global (auth + books)
- **TanStack Query** para cache inteligente e queries
- **Persistência automática** no localStorage
- **Invalidação de cache** otimizada

### ✅ **WebSocket em Tempo Real**
- **Cliente WebSocket** robusto com reconexão automática
- **Notificações push** para geração de livros
- **Status de conexão** visível no dashboard
- **Hooks personalizados** para easy integration

### ✅ **Tipos TypeScript Alinhados**
- **100% alinhado** com schemas do backend
- **Enums** para UserRole, UserStatus, BookStatus, BookStyle
- **Validações Zod** espelhando as regras do backend
- **Constantes de validação** (5-20 páginas, etc.)

### ✅ **Formulários Robustos**
- **React Hook Form + Zod** para validações
- **Indicador de força** de senha no registro
- **Validações client-side** alinhadas com backend
- **Tratamento de erros** padronizado

### ✅ **App Router Next.js 15 Otimizado**
- **Route groups**: `(auth)` e `(dashboard)`
- **Layouts específicos** para cada seção
- **Server e Client Components** bem definidos
- **Middleware de proteção** automática

### ✅ **Componentes UI Modernos**
- **BookReader** com navegação e tela cheia
- **BookGrid** com estados de loading
- **Dashboard completo** com estatísticas
- **Sistema de notificações** em tempo real
- **User menu** com roles e permissões

## 🛡️ **Segurança Implementada**
- JWT tokens com refresh automático
- Proteção CSRF preparada
- Validações client e server-side
- Error boundaries para captura de erros
- Rate limiting preparado

## 📱 **UX/UI Aprimorada**
- Design Aceternity UI style
- Estados de loading consistentes
- Notificações toast integradas
- Navegação intuitiva
- Responsividade completa

## 🔧 **Tecnologias Utilizadas**
- **Next.js 15** (App Router)
- **React 19** (Server/Client Components)
- **TypeScript 5**
- **TanStack Query** (Server State)
- **Zustand** (Global State)
- **Tailwind CSS 4**
- **React Hook Form + Zod**
- **WebSocket** (Real-time)
- **Sonner** (Toast Notifications)

## 🚀 **Como Executar**

```bash
# Instalar dependências
pnpm install

# Modo desenvolvimento
pnpm dev

# Build para produção
pnpm build

# Executar produção
pnpm start
```

## 🌐 **Variáveis de Ambiente**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 **Estrutura de Arquivos**

```
frontend/
├── app/                          # App Router
│   ├── (auth)/                  # Route group - Auth
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/             # Route group - Dashboard
│   │   ├── books/
│   │   ├── profile/
│   │   └── settings/
│   └── globals.css
├── components/                   # Componentes UI
│   ├── forms/                   # Formulários
│   ├── ui/                      # Componentes base
│   └── dashboard/               # Componentes do dashboard
├── hooks/                       # Hooks customizados
├── lib/                         # Utilitários
│   ├── auth/                    # Sistema de autenticação
│   ├── queries/                 # TanStack Query queries
│   ├── stores/                  # Zustand stores
│   ├── types/                   # Definições TypeScript
│   ├── validation/              # Schemas Zod
│   └── realtime/               # WebSocket client
└── middleware.ts               # Middleware de proteção
```

## 🔄 **Fluxos Principais**

### Autenticação
1. Usuario acessa `/login` ou `/register`
2. Formulário valida dados com Zod
3. Request para backend `/api/v1/auth/login`
4. JWT token armazenado + estado Zustand
5. Redirect automático para dashboard
6. Middleware protege rotas privadas

### Criação de Livro
1. Usuario acessa `/dashboard/books/create`
2. Preenche formulário (validação em tempo real)
3. Request para `/api/v1/books` (POST)
4. Inicia task Celery no backend
5. WebSocket recebe updates em tempo real
6. Notificações mostram progresso
7. Redirect para livro quando completo

### Notificações em Tempo Real
1. WebSocket conecta automaticamente após login
2. Backend envia updates via notification_service
3. Frontend processa mensagens por tipo
4. Toast notifications aparecem automaticamente
5. Estado de livros atualiza em tempo real

## 🧪 **Testes** (Preparado)
- Jest + Testing Library configurado
- MSW para mock de APIs
- Estrutura de testes organizada

## ⚡ **Performance**
- Cache inteligente com TanStack Query
- Lazy loading de componentes
- Otimizações do Next.js 15
- Bundle splitting automático

## 🎯 **Próximos Passos**
1. Implementar testes automatizados
2. Adicionar PWA capabilities
3. Otimizar para SEO
4. Implementar analytics
5. Adicionar mais componentes UI

---

**Status**: ✅ **Produção Ready**
**Integração Backend**: ✅ **100% Integrada**
**WebSocket**: ✅ **Funcionando**
**Autenticação**: ✅ **Completa**