# 🚨 Sistema de Exceções Customizadas

## 📋 Visão Geral

Este sistema fornece um tratamento robusto e padronizado de erros para toda a aplicação, substituindo o uso direto de `HTTPException` por exceções customizadas type-safe.

## 🎯 Benefícios

- ✅ **Padronização**: Todas as respostas de erro seguem o mesmo formato
- ✅ **Type Safety**: Exceções tipadas com códigos de erro específicos  
- ✅ **Debugging**: Logs estruturados com contexto completo
- ✅ **Rastreabilidade**: Request ID único para cada requisição
- ✅ **Manutenibilidade**: Centralização do tratamento de erros

## 🏗️ Arquitetura

```
app/exceptions/
├── __init__.py              # Exports principais
├── base_exceptions.py       # Exceções base e específicas
├── http_exceptions.py       # Handlers HTTP e helpers
├── examples.py             # Exemplos de uso
└── README.md               # Este guia

app/middleware/
├── __init__.py              # Exports de middlewares
└── exception_middleware.py # Middleware global
```

## 📊 Formato de Resposta Padronizada

```json
{
  "error": {
    "message": "Mensagem para o usuário",
    "code": "ERROR_CODE_ENUM",
    "status_code": 400,
    "details": {
      "field": "campo_com_erro",
      "provided_value": "valor_inválido"
    },
    "request_id": "uuid-da-requisição"
  }
}
```

## 🎨 Exceções Disponíveis

### Base Classes
- `AppException` - Exceção base da aplicação
- `ValidationError` - Erros de validação de dados
- `AuthenticationError` - Falhas de autenticação  
- `AuthorizationError` - Problemas de permissão
- `NotFoundError` - Recursos não encontrados
- `ConflictError` - Conflitos de dados
- `BusinessRuleError` - Violações de regras de negócio
- `ExternalServiceError` - Falhas em serviços externos

### Exceções Específicas
- `UserNotFoundError` - Usuário não encontrado
- `BookNotFoundError` - Livro não encontrado
- `EmailAlreadyExistsError` - Email duplicado
- `InvalidBookPagesError` - Páginas fora do limite (5-20)
- `UserBookLimitError` - Limite de livros excedido
- `InvalidPasswordError` - Senha não atende critérios

## 🚀 Como Usar

### 1. Import das Exceções

```python
from app.exceptions.base_exceptions import (
    UserNotFoundError,
    BookNotFoundError,
    EmailAlreadyExistsError,
    InvalidBookPagesError,
    AuthorizationError
)
```

### 2. Lançar Exceções nos Services

```python
# ❌ ANTES (HTTPException direta)
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuário não encontrado"
    )

# ✅ DEPOIS (Exceção customizada)
if not user:
    raise UserNotFoundError(user_id)
```

### 3. Helpers para Simplificar

```python
from app.exceptions.http_exceptions import (
    raise_not_found,
    raise_validation_error,
    raise_authorization_error
)

# Uso simplificado
raise_not_found("user", user_id)
raise_validation_error("email", "Formato inválido", user_data.email)
raise_authorization_error("book", "view_permission")
```

### 4. Validações de Negócio

```python
# Regra: Livros devem ter 5-20 páginas
if not 5 <= book_data.pages_count <= 20:
    raise InvalidBookPagesError(book_data.pages_count)

# Limite de livros por usuário
if book_count >= max_limit:
    raise UserBookLimitError(book_count, max_limit)
```

## 📝 Codes de Erro Padronizados

### Validação
- `VALIDATION_ERROR` - Erro genérico de validação
- `REQUIRED_FIELD_MISSING` - Campo obrigatório ausente
- `INVALID_FORMAT` - Formato inválido
- `INVALID_VALUE` - Valor inválido

### Autenticação
- `INVALID_CREDENTIALS` - Credenciais incorretas
- `TOKEN_EXPIRED` - Token expirado
- `USER_INACTIVE` - Usuário inativo

### Autorização  
- `INSUFFICIENT_PERMISSIONS` - Sem permissão
- `ACCESS_DENIED` - Acesso negado
- `RESOURCE_FORBIDDEN` - Recurso proibido

### Recursos
- `USER_NOT_FOUND` - Usuário não encontrado
- `BOOK_NOT_FOUND` - Livro não encontrado
- `RESOURCE_NOT_FOUND` - Recurso genérico não encontrado

### Negócio
- `BOOK_PAGES_LIMIT_EXCEEDED` - Limite de páginas excedido
- `USER_BOOK_LIMIT_EXCEEDED` - Limite de livros excedido
- `INVALID_BOOK_STATUS` - Status inválido para operação

## 🔧 Logging Automático

O sistema inclui logging automático com:

- **Request ID único** para rastreabilidade
- **Tempo de processamento** da requisição  
- **IP do cliente** (considerando proxies)
- **Contexto completo** do erro
- **Stack trace** para erros internos

### Headers de Resposta

```
X-Request-ID: uuid-único
X-Process-Time: 0.123
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

## 🧪 Testando Exceções

```python
import pytest
from app.exceptions.base_exceptions import UserNotFoundError

def test_user_not_found_exception():
    with pytest.raises(UserNotFoundError) as exc_info:
        raise UserNotFoundError(user_id=123)
    
    error = exc_info.value
    assert error.status_code == 404
    assert error.error_code == ErrorCode.USER_NOT_FOUND
    assert "123" in str(error.details)
```

## 🚦 Middleware de Tratamento

O `ExceptionMiddleware` automaticamente:

1. **Captura** todas as exceções não tratadas
2. **Converte** em respostas JSON padronizadas  
3. **Adiciona** logging estruturado
4. **Inclui** request ID e métricas
5. **Mantém** stack trace para debugging

## 📈 Monitoramento

Logs incluem métricas para monitoramento:

```python
logger.info(
    f"Request completed: {method} {path} - {status_code}",
    extra={
        "request_id": request_id,
        "status_code": status_code, 
        "process_time": 0.123,
        "error_code": "USER_NOT_FOUND"  # se erro
    }
)
```

## 🔄 Migração Gradual

Para migrar código existente:

1. **Identificar** HTTPExceptions nos services
2. **Substituir** por exceções customizadas apropriadas
3. **Testar** respostas de erro
4. **Verificar** logs estruturados

## 💡 Boas Práticas

- ✅ Use exceções específicas quando disponíveis
- ✅ Inclua contexto útil nos details
- ✅ Preserve informações para debugging
- ✅ Não exponha dados sensíveis em mensagens
- ✅ Use helpers quando apropriado
- ❌ Não capture exceções desnecessariamente
- ❌ Não use HTTPException diretamente nos services