'use client'

import { toast } from 'sonner'
import { APIErrorClass, isAPIError } from './types/api'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface FetchOptions extends RequestInit {
  token?: string
  skipAuth?: boolean
  skipErrorToast?: boolean
}

interface APIClient {
  get: <T = unknown>(endpoint: string, options?: FetchOptions) => Promise<T>
  post: <T = unknown>(endpoint: string, data?: unknown, options?: FetchOptions) => Promise<T>
  put: <T = unknown>(endpoint: string, data?: unknown, options?: FetchOptions) => Promise<T>
  delete: <T = unknown>(endpoint: string, options?: FetchOptions) => Promise<T>
  patch: <T = unknown>(endpoint: string, data?: unknown, options?: FetchOptions) => Promise<T>
}

// Token management
let currentToken: string | null = null
let tokenRefreshPromise: Promise<string> | null = null

const getStoredToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

const setStoredToken = (token: string | null): void => {
  if (typeof window === 'undefined') return
  if (token) {
    localStorage.setItem('access_token', token)
  } else {
    localStorage.removeItem('access_token')
  }
  currentToken = token
}

const refreshToken = async (): Promise<string> => {
  if (tokenRefreshPromise) {
    return tokenRefreshPromise
  }

  tokenRefreshPromise = (async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${currentToken || getStoredToken()}`,
        },
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data = await response.json()
      const newToken = data.access_token

      setStoredToken(newToken)
      return newToken
    } catch (error) {
      // Token refresh failed, clear stored token and redirect to login
      setStoredToken(null)
      if (typeof window !== 'undefined') {
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
      }
      throw error
    } finally {
      tokenRefreshPromise = null
    }
  })()

  return tokenRefreshPromise
}

// Core fetch function with automatic token handling
export async function fetchAPI<T = unknown>(
  endpoint: string, 
  options: FetchOptions = {}
): Promise<T> {
  const { 
    token, 
    skipAuth = false, 
    skipErrorToast = false,
    headers, 
    ...rest 
  } = options

  // Get token from parameter, current token, or storage
  let authToken = token || currentToken || (skipAuth ? null : getStoredToken())

  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(authToken && !skipAuth ? { Authorization: `Bearer ${authToken}` } : {}),
    ...(headers as Record<string, string>),
  }

  let response: Response

  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      headers: defaultHeaders,
      ...rest,
    })
  } catch (error) {
    const message = 'Erro de conectividade. Verifique sua conexão com a internet.'
    if (!skipErrorToast) {
      toast.error(message)
    }
    throw new APIErrorClass(message, 0)
  }

  // Handle 401 - try token refresh if we have a token
  if (response.status === 401 && authToken && !skipAuth) {
    try {
      const newToken = await refreshToken()
      
      // Retry the request with new token
      const retryHeaders = {
        ...defaultHeaders,
        Authorization: `Bearer ${newToken}`,
      }

      response = await fetch(`${API_URL}${endpoint}`, {
        headers: retryHeaders,
        ...rest,
      })
    } catch (refreshError) {
      // Refresh failed, let the original 401 be handled below
    }
  }

  // Handle error responses
  if (!response.ok) {
    let errorData: any = {}
    
    try {
      errorData = await response.json()
    } catch {
      errorData = { detail: 'Erro desconhecido do servidor' }
    }

    const apiError = new APIErrorClass(
      errorData.detail || `Erro ${response.status}`,
      response.status,
      errorData.field,
      errorData.error_code,
      errorData.details
    )

    // Show error toast unless explicitly disabled
    if (!skipErrorToast) {
      const errorMessage = apiError.message || 'Algo deu errado. Tente novamente.'
      
      if (response.status >= 500) {
        toast.error('Erro interno do servidor. Nossa equipe foi notificada.')
      } else if (response.status === 429) {
        toast.error('Muitas tentativas. Aguarde um momento antes de tentar novamente.')
      } else {
        toast.error(errorMessage)
      }
    }

    throw apiError
  }

  // Handle empty responses (e.g. 204 No Content)
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return null as T
  }

  try {
    return await response.json()
  } catch (error) {
    throw new APIErrorClass('Resposta inválida do servidor', 502)
  }
}

// API client with convenient methods
export const api: APIClient = {
  get: <T = unknown>(endpoint: string, options?: FetchOptions) =>
    fetchAPI<T>(endpoint, { ...options, method: 'GET' }),

  post: <T = unknown>(endpoint: string, data?: unknown, options?: FetchOptions) =>
    fetchAPI<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T = unknown>(endpoint: string, data?: unknown, options?: FetchOptions) =>
    fetchAPI<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T = unknown>(endpoint: string, options?: FetchOptions) =>
    fetchAPI<T>(endpoint, { ...options, method: 'DELETE' }),

  patch: <T = unknown>(endpoint: string, data?: unknown, options?: FetchOptions) =>
    fetchAPI<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),
}

// File upload helper
export const uploadFile = async (
  endpoint: string,
  file: File,
  options?: FetchOptions
): Promise<any> => {
  const { token, headers, ...rest } = options || {}
  
  const authToken = token || currentToken || getStoredToken()
  const formData = new FormData()
  formData.append('file', file)

  const uploadHeaders: Record<string, string> = {
    ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    ...(headers as Record<string, string>),
  }

  // Don't set Content-Type for FormData, let browser handle it
  delete uploadHeaders['Content-Type']

  const response = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: uploadHeaders,
    body: formData,
    ...rest,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new APIErrorClass(
      errorData.detail || 'Upload failed',
      response.status,
      errorData.field,
      errorData.error_code,
      errorData.details
    )
  }

  return response.json()
}

// Download helper
export const downloadFile = async (
  endpoint: string,
  filename?: string,
  options?: FetchOptions
): Promise<void> => {
  const { token, ...rest } = options || {}
  const authToken = token || currentToken || getStoredToken()

  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    },
    ...rest,
  })

  if (!response.ok) {
    throw new APIErrorClass('Download failed', response.status)
  }

  const blob = await response.blob()
  
  if (typeof window !== 'undefined') {
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'download'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }
}

// Utility functions
export const setAuthToken = (token: string | null): void => {
  setStoredToken(token)
}

export const getAuthToken = (): string | null => {
  return currentToken || getStoredToken()
}

export const clearAuthToken = (): void => {
  setStoredToken(null)
}
