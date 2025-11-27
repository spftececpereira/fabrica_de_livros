# 📋 **VALIDAÇÕES DE NEGÓCIO IMPLEMENTADAS**

## 🎯 **Visão Geral**

Este documento detalha todas as validações de negócio implementadas nos modelos da Fábrica de Livros v2, baseadas nas especificações do PRD.

---

## 📚 **MODELO BOOK**

### **Regras Críticas do PRD**
- ✅ **5-20 páginas por livro** (regra fundamental)
- ✅ **4 estilos suportados**: cartoon, realistic, manga, classic
- ✅ **Controle de status** com transições válidas
- ✅ **Títulos únicos e descritivos**

### **Validações Implementadas**

#### **📖 Título**
```python
@validates('title')
def validate_title(self, key, title: str) -> str:
```
- **Obrigatório**: Não pode ser nulo ou vazio
- **Comprimento**: 3-200 caracteres
- **Sanitização**: Remove espaços extras automaticamente

#### **📄 Descrição**
```python
@validates('description') 
def validate_description(self, key, description: Optional[str]) -> Optional[str]:
```
- **Opcional**: Pode ser nula
- **Comprimento**: Máximo 1000 caracteres
- **Sanitização**: Remove espaços desnecessários

#### **📊 Quantidade de Páginas (CRÍTICA)**
```python
@validates('pages_count')
def validate_pages_count(self, key, pages_count: int) -> int:
```
- **Regra PRD**: Entre 5 e 20 páginas obrigatoriamente
- **Tipo**: Deve ser número inteiro
- **Exceção**: `InvalidBookPagesError` para violações

#### **🎨 Estilo**
```python
@validates('style')
def validate_style(self, key, style: str) -> str:
```
- **Valores permitidos**: `cartoon`, `realistic`, `manga`, `classic`
- **Obrigatório**: Não pode ser nulo
- **Case sensitive**: Deve ser exatamente como especificado

#### **🔄 Status com Transições Controladas**
```python
@validates('status')
def validate_status(self, key, status: str) -> str:
```

**Estados válidos:**
- `draft` → Rascunho inicial
- `processing` → Em geração de conteúdo
- `completed` → Finalizado com sucesso
- `failed` → Falha na geração

**Transições permitidas:**
```
draft ──────→ processing ──────→ completed
  ↑               │                   │
  └───────────────┼───────────────────┘
                  ↓
               failed ────────→ draft
```

### **Propriedades Híbridas**

#### **Estado do Livro**
```python
@hybrid_property
def is_editable(self) -> bool:
    """Editável apenas em draft ou failed"""

@hybrid_property  
def can_generate_pdf(self) -> bool:
    """PDF apenas se completed e todas páginas criadas"""
```

#### **Validações de Negócio**
```python
def validate_business_rules(self) -> None:
    """Valida se páginas criadas = páginas esperadas"""
```

### **Constraints de Banco**
```sql
-- Páginas válidas (5-20)
CHECK (pages_count >= 5 AND pages_count <= 20)

-- Status válidos  
CHECK (status IN ('draft', 'processing', 'completed', 'failed'))

-- Estilos válidos
CHECK (style IN ('cartoon', 'realistic', 'manga', 'classic'))

-- Título mínimo
CHECK (LENGTH(title) >= 3)
```

---

## 👤 **MODELO USER**

### **Regras de Negócio**
- ✅ **Sistema de roles**: user, premium, admin
- ✅ **Limites por plano**: 5/50/999999 livros
- ✅ **Email único e validado**
- ✅ **Controle de status e ativação**

### **Validações Implementadas**

#### **📧 Email (CRÍTICA)**
```python
@validates('email')
def validate_email(self, key, email: str) -> str:
```
- **Formato RFC**: Regex completo para validação
- **Normalização**: Lowercase automático
- **Unicidade**: Garantida por constraint
- **Segurança**: Bloqueia domínios temporários
- **Limite**: Máximo 255 caracteres

#### **👤 Nome Completo**
```python
@validates('full_name')
def validate_full_name(self, key, full_name: str) -> str:
```
- **Obrigatório**: Não pode ser vazio
- **Comprimento**: 2-100 caracteres
- **Caracteres**: Apenas letras, espaços, hífen, ponto, aspas
- **Unicode**: Suporta acentos (À-ÿ)

#### **🔑 Roles e Permissões**
```python
@validates('role')
def validate_role(self, key, role: str) -> str:
```

**Hierarquia de roles:**
```
user ────→ premium ────→ admin
 5 livros    50 livros    ilimitado
```

**Limites por role:**
```python
@hybrid_property
def max_books_allowed(self) -> int:
    limits = {
        UserRole.USER: 5,      # Usuário gratuito
        UserRole.PREMIUM: 50,   # Plano pago
        UserRole.ADMIN: 999999  # Sem limite
    }
```

#### **🔐 Validação de Hash de Senha**
```python
@validates('password_hash')
def validate_password_hash(self, key, password_hash: str) -> str:
```
- **Obrigatório**: Não pode ser nulo
- **Formato**: Deve parecer hash válido (>50 chars)
- **Segurança**: Valida se é realmente um hash

#### **📊 Status do Usuário**
```python
@validates('status')
def validate_status(self, key, status: str) -> str:
```

**Estados válidos:**
- `active` → Usuário ativo normal
- `inactive` → Usuário desativado
- `suspended` → Usuário suspenso (violação)
- `pending` → Aguardando verificação

### **Propriedades de Negócio**

#### **Permissões por Role**
```python
@hybrid_property
def is_admin(self) -> bool:
    """Verifica se é administrador"""

@hybrid_property
def is_premium(self) -> bool:
    """Verifica se tem plano premium ou admin"""

@hybrid_property
def can_create_books(self) -> bool:
    """Pode criar livros se ativo"""

@hybrid_property
def can_create_more_books(self) -> bool:
    """Verifica se não atingiu limite"""
```

#### **Sistema de Permissões**
```python
def can_perform_action(self, action: str) -> bool:
    """Sistema flexível de permissões por ação"""
    action_permissions = {
        'create_book': self.can_create_books and self.can_create_more_books,
        'edit_book': self.can_create_books,
        'delete_book': self.can_create_books,
        'admin_actions': self.is_admin,
        'premium_features': self.is_premium
    }
```

### **Constraints de Banco**
```sql
-- Email válido
CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')

-- Nome mínimo  
CHECK (LENGTH(full_name) >= 2)

-- Role válido
CHECK (role IN ('user', 'premium', 'admin'))

-- Status válido
CHECK (status IN ('active', 'inactive', 'suspended', 'pending'))
```

---

## 📄 **MODELO PAGE**

### **Regras de Conteúdo**
- ✅ **Sequência numérica** de páginas por livro
- ✅ **Conteúdo limitado** e sanitizado
- ✅ **URLs de imagem** válidas

### **Validações Implementadas**

#### **📊 Número da Página**
```python
@validates('page_number')
def validate_page_number(self, key, page_number: int) -> int:
```
- **Positivo**: Deve ser > 0
- **Sequencial**: Não pode exceder pages_count do livro
- **Único**: Uma página por número por livro

#### **📝 Conteúdo de Texto**
```python
@validates('text_content')
def validate_text_content(self, key, text_content: Optional[str]) -> Optional[str]:
```
- **Opcional**: Pode ser nulo
- **Limite**: Máximo 2000 caracteres
- **Sanitização**: Remove espaços extras

#### **🖼️ URL de Imagem**
```python
@validates('image_url')
def validate_image_url(self, key, image_url: Optional[str]) -> Optional[str]:
```
- **Formato**: Deve ser URL válida (http/https)
- **Opcional**: Pode ser nula
- **Sanitização**: Remove espaços

#### **🤖 Prompt de IA**
```python
@validates('image_prompt')
def validate_image_prompt(self, key, image_prompt: Optional[str]) -> Optional[str]:
```
- **Limite**: Máximo 1000 caracteres
- **Opcional**: Para geração de imagens

### **Propriedades de Conteúdo**
```python
@hybrid_property
def has_content(self) -> bool:
    """Tem texto OU imagem"""

@hybrid_property
def is_complete(self) -> bool:  
    """Tem texto E imagem"""
```

### **Constraints de Banco**
```sql
-- Página positiva
CHECK (page_number > 0)

-- Texto limitado
CHECK (LENGTH(text_content) <= 2000)

-- Prompt limitado  
CHECK (LENGTH(image_prompt) <= 1000)

-- Unicidade por livro
UNIQUE(book_id, page_number)
```

---

## 🛠️ **UTILITÁRIOS DE VALIDAÇÃO**

### **Validadores Centralizados**

#### **Email e Segurança**
```python
validate_email_format(email: str) -> str
validate_password_strength(password: str) -> None
```

#### **Regras de Livro**
```python
validate_book_pages(pages_count: int) -> None
validate_book_style(style: str) -> None
validate_book_status_transition(current: str, new: str) -> None
```

#### **Arquivos e URLs**
```python
validate_file_extension(filename: str, allowed: List[str]) -> None
validate_url_format(url: str) -> str
sanitize_text(text: str, max_length: Optional[int]) -> str
```

#### **Permissões**
```python
validate_user_role_permissions(user_role: str, required_role: str) -> None
```

---

## 🔐 **REGRAS DE SEGURANÇA**

### **Validação de Senha Forte**
```python
# Critérios obrigatórios:
- Mínimo 8 caracteres
- Máximo 128 caracteres  
- Pelo menos 1 minúscula
- Pelo menos 1 maiúscula
- Pelo menos 1 número
- Pelo menos 1 caractere especial
- Não conter padrões fracos (123456, password, etc)
```

### **Sanitização de Dados**
- **Emails**: Normalização automática (lowercase)
- **Textos**: Remoção de caracteres de controle
- **URLs**: Validação de protocolo e formato
- **Nomes**: Apenas caracteres seguros

### **Proteções de Banco**
- **Constraints**: Validações duplicadas no PostgreSQL
- **Índices**: Performance em consultas frequentes
- **Unicidade**: Garantias de integridade

---

## 📊 **ÍNDICES DE PERFORMANCE**

### **Books**
- `idx_user_status` - Busca por usuário e status
- `idx_created_status` - Timeline de criação

### **Users**  
- `idx_email_status` - Login e verificação
- `idx_role_active` - Permissões por role
- `idx_created_at` - Auditoria temporal

### **Pages**
- `idx_book_page_unique` - Unicidade sequencial
- `idx_book_page_order` - Ordenação por livro

---

## ✅ **RESUMO DE CONFORMIDADE PRD**

| Regra PRD | Status | Implementação |
|-----------|--------|---------------|
| 5-20 páginas | ✅ | Model + Constraint + Exception |
| 4 estilos | ✅ | Enum + Validation + Constraint |
| Status controlado | ✅ | State machine + Transitions |
| Roles/Limites | ✅ | Hierarchy + Permissions |
| Email único | ✅ | Constraint + Validation |
| Segurança | ✅ | Password + Sanitization |
| Performance | ✅ | Indexes + Optimization |

**100% das regras críticas do PRD implementadas e testadas.**