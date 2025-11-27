'use client'

import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from 'sonner'
import { queryClient } from '../query-client'
import { useAuth } from '../queries/auth-queries'
import { useAuthStore } from '../stores/auth-store'
import { getAuthToken } from '../api'

interface AuthContextType {
  user: any
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: any) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
  refetchUser: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

function AuthProviderInner({ children }: AuthProviderProps) {
  const auth = useAuth()
  const { setUser, setLoading } = useAuthStore()

  useEffect(() => {
    // Check if user is already logged in on mount
    const token = getAuthToken()
    
    if (token && !auth.user) {
      // Token exists but no user in store, try to fetch user
      auth.refetchUser()
    } else if (!token && auth.user) {
      // No token but user in store, clear user
      setUser(null)
    } else {
      // No token and no user, or both exist - set loading to false
      setLoading(false)
    }
  }, []) // Empty dependency array - only run on mount

  const contextValue: AuthContextType = {
    user: auth.user,
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    login: auth.login,
    register: auth.register,
    logout: auth.logout,
    refetchUser: auth.refetchUser,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

export function AuthProvider({ children }: AuthProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProviderInner>
        {children}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'hsl(var(--background))',
              color: 'hsl(var(--foreground))',
              border: '1px solid hsl(var(--border))',
            },
          }}
        />
      </AuthProviderInner>
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  )
}

export function useAuthContext() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }
  return context
}