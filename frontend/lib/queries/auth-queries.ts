'use client'

import { useMutation, useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { api, setAuthToken, clearAuthToken } from '../api'
import { queryKeys, invalidateQueries } from '../query-client'
import { useAuthStore } from '../stores/auth-store'
import { 
  LoginRequest, 
  TokenResponse, 
  User, 
  UserCreate, 
  UserUpdate,
  ChangePasswordRequest 
} from '../types/user'

// Login mutation
export const useLogin = () => {
  const setUser = useAuthStore(state => state.setUser)
  
  return useMutation({
    mutationFn: async (credentials: LoginRequest): Promise<TokenResponse> => {
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      return api.post<TokenResponse>('/api/v1/auth/login', formData, {
        headers: {
          // Let the browser set Content-Type for FormData
          'Content-Type': undefined as any,
        },
      })
    },
    onSuccess: (data) => {
      setAuthToken(data.access_token)
      setUser(data.user)
      toast.success('Login realizado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao fazer login')
    },
  })
}

// Register mutation
export const useRegister = () => {
  const setUser = useAuthStore(state => state.setUser)
  
  return useMutation({
    mutationFn: async (userData: UserCreate): Promise<TokenResponse> => {
      return api.post<TokenResponse>('/api/v1/auth/register', userData)
    },
    onSuccess: (data) => {
      setAuthToken(data.access_token)
      setUser(data.user)
      toast.success('Conta criada com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao criar conta')
    },
  })
}

// Logout mutation
export const useLogout = () => {
  const logout = useAuthStore(state => state.logout)
  
  return useMutation({
    mutationFn: async () => {
      // Call backend logout endpoint (optional)
      try {
        await api.post('/api/v1/auth/logout', {}, { skipErrorToast: true })
      } catch {
        // Ignore errors, we're logging out anyway
      }
    },
    onSuccess: () => {
      clearAuthToken()
      logout()
      toast.success('Logout realizado com sucesso!')
    },
    onSettled: () => {
      // Always clear local state even if backend call fails
      clearAuthToken()
      logout()
    },
  })
}

// Get current user query
export const useCurrentUser = () => {
  const { setUser, setLoading, user, isAuthenticated } = useAuthStore()
  
  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: async (): Promise<User> => {
      return api.get<User>('/api/v1/auth/me')
    },
    enabled: isAuthenticated && !!user,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: (failureCount, error: any) => {
      // Don't retry on 401 (user not authenticated)
      if (error?.status === 401) {
        return false
      }
      return failureCount < 2
    },
    onSuccess: (data) => {
      setUser(data)
      setLoading(false)
    },
    onError: (error: any) => {
      if (error?.status === 401) {
        // Token is invalid, clear auth state
        clearAuthToken()
        setUser(null)
      }
      setLoading(false)
    },
  })
}

// Refresh token mutation
export const useRefreshToken = () => {
  const setUser = useAuthStore(state => state.setUser)
  
  return useMutation({
    mutationFn: async (): Promise<TokenResponse> => {
      return api.post<TokenResponse>('/api/v1/auth/refresh')
    },
    onSuccess: (data) => {
      setAuthToken(data.access_token)
      setUser(data.user)
    },
    onError: () => {
      // Refresh failed, clear auth state
      clearAuthToken()
      setUser(null)
    },
  })
}

// Update profile mutation
export const useUpdateProfile = () => {
  const updateUser = useAuthStore(state => state.updateUser)
  
  return useMutation({
    mutationFn: async (updates: UserUpdate): Promise<User> => {
      return api.put<User>('/api/v1/auth/me', updates)
    },
    onSuccess: (data) => {
      updateUser(data)
      invalidateQueries.auth()
      toast.success('Perfil atualizado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao atualizar perfil')
    },
  })
}

// Change password mutation
export const useChangePassword = () => {
  return useMutation({
    mutationFn: async (passwords: ChangePasswordRequest): Promise<void> => {
      return api.post('/api/v1/auth/change-password', passwords)
    },
    onSuccess: () => {
      toast.success('Senha alterada com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao alterar senha')
    },
  })
}

// Verify email mutation (if implemented in backend)
export const useVerifyEmail = () => {
  return useMutation({
    mutationFn: async (token: string): Promise<void> => {
      return api.post('/api/v1/auth/verify-email', { token })
    },
    onSuccess: () => {
      toast.success('Email verificado com sucesso!')
      invalidateQueries.auth()
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao verificar email')
    },
  })
}

// Request password reset mutation (if implemented in backend)
export const useRequestPasswordReset = () => {
  return useMutation({
    mutationFn: async (email: string): Promise<void> => {
      return api.post('/api/v1/auth/request-password-reset', { email })
    },
    onSuccess: () => {
      toast.success('Email de recuperação enviado!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao enviar email de recuperação')
    },
  })
}

// Reset password mutation (if implemented in backend)
export const useResetPassword = () => {
  return useMutation({
    mutationFn: async ({ token, new_password }: { token: string; new_password: string }): Promise<void> => {
      return api.post('/api/v1/auth/reset-password', { token, new_password })
    },
    onSuccess: () => {
      toast.success('Senha redefinida com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao redefinir senha')
    },
  })
}

// Custom hook for auth state
export const useAuth = () => {
  const authStore = useAuthStore()
  const currentUserQuery = useCurrentUser()
  const loginMutation = useLogin()
  const registerMutation = useRegister()
  const logoutMutation = useLogout()
  
  return {
    // State
    user: authStore.user,
    isAuthenticated: authStore.isAuthenticated,
    isLoading: authStore.isLoading || currentUserQuery.isLoading,
    
    // Mutations
    login: loginMutation.mutateAsync,
    register: registerMutation.mutateAsync,
    logout: logoutMutation.mutate,
    
    // Mutation states
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    
    // Query
    refetchUser: currentUserQuery.refetch,
    
    // Store actions
    setUser: authStore.setUser,
    updateUser: authStore.updateUser,
  }
}