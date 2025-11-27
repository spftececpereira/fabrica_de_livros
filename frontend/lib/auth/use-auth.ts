'use client'

import { useAuthContext } from './auth-provider'
import { useAuthStore } from '../stores/auth-store'
import { userHelpers } from '../types/user'

export function useAuth() {
  const context = useAuthContext()
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  const { user } = context

  // Add computed properties to user
  const userWithHelpers = user ? {
    ...user,
    isAdmin: userHelpers.isAdmin(user),
    isPremium: userHelpers.isPremium(user),
    canCreateBooks: userHelpers.canCreateBooks(user),
    maxBooksAllowed: userHelpers.maxBooksAllowed(user),
  } : null

  return {
    ...context,
    user: userWithHelpers,
  }
}

// Hook for accessing just the user object
export function useUser() {
  const { user } = useAuth()
  return user
}

// Hook for checking specific permissions
export function usePermissions() {
  const { user, isAuthenticated } = useAuth()

  return {
    canCreateBooks: user?.canCreateBooks || false,
    canEditBooks: user?.canCreateBooks || false,
    canDeleteBooks: user?.canCreateBooks || false,
    canGeneratePDF: isAuthenticated,
    canAccessAdmin: user?.isAdmin || false,
    canAccessPremium: user?.isPremium || false,
    hasReachedBookLimit: user ? 
      (user.books_count || 0) >= (user.maxBooksAllowed || 0) : false,
  }
}

// Hook for auth loading states
export function useAuthLoading() {
  const { isLoading } = useAuth()
  const authStore = useAuthStore()
  
  return {
    isLoading,
    isInitialLoading: authStore.isLoading,
  }
}