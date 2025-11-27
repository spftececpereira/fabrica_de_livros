'use client'

import { QueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

// Default stale time: 5 minutes
const DEFAULT_STALE_TIME = 1000 * 60 * 5

// Default cache time: 10 minutes  
const DEFAULT_CACHE_TIME = 1000 * 60 * 10

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: DEFAULT_STALE_TIME,
      gcTime: DEFAULT_CACHE_TIME,
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        // Retry up to 3 times for other errors
        return failureCount < 3
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      refetchOnReconnect: 'always',
    },
    mutations: {
      retry: (failureCount, error: any) => {
        // Don't retry mutations on client errors
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        // Retry once for server errors
        return failureCount < 1
      },
      onError: (error: any) => {
        // Global error handling for mutations
        const message = error?.message || error?.detail || 'Algo deu errado. Tente novamente.'
        toast.error(message)
      },
    },
  },
})

// Query Keys Factory
export const queryKeys = {
  // Auth
  auth: {
    me: ['auth', 'me'] as const,
    refresh: ['auth', 'refresh'] as const,
  },
  
  // Books
  books: {
    all: ['books'] as const,
    lists: () => [...queryKeys.books.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => 
      [...queryKeys.books.lists(), { ...filters }] as const,
    details: () => [...queryKeys.books.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.books.details(), id] as const,
    stats: () => [...queryKeys.books.all, 'stats'] as const,
    recent: () => [...queryKeys.books.all, 'recent'] as const,
    search: (term: string) => [...queryKeys.books.all, 'search', term] as const,
    generation: {
      status: (taskId: string) => ['books', 'generation', 'status', taskId] as const,
    },
  },

  // Users
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (filters?: Record<string, unknown>) => 
      [...queryKeys.users.lists(), { ...filters }] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.users.details(), id] as const,
  },

  // Badges
  badges: {
    all: ['badges'] as const,
    user: (userId: number) => [...queryKeys.badges.all, 'user', userId] as const,
    available: () => [...queryKeys.badges.all, 'available'] as const,
  },

  // Health
  health: {
    status: ['health', 'status'] as const,
  },
} as const

// Invalidation helpers
export const invalidateQueries = {
  auth: () => queryClient.invalidateQueries({ queryKey: queryKeys.auth.me }),
  
  books: {
    all: () => queryClient.invalidateQueries({ queryKey: queryKeys.books.all }),
    lists: () => queryClient.invalidateQueries({ queryKey: queryKeys.books.lists() }),
    detail: (id: number) => queryClient.invalidateQueries({ queryKey: queryKeys.books.detail(id) }),
    stats: () => queryClient.invalidateQueries({ queryKey: queryKeys.books.stats() }),
  },
  
  badges: {
    all: () => queryClient.invalidateQueries({ queryKey: queryKeys.badges.all }),
    user: (userId: number) => queryClient.invalidateQueries({ queryKey: queryKeys.badges.user(userId) }),
  },
}

// Pre-configured query options
export const queryOptions = {
  // Fast refetch for real-time data
  realtime: {
    staleTime: 0,
    gcTime: 1000 * 60 * 2, // 2 minutes
    refetchInterval: 5000, // 5 seconds
  },
  
  // Long cache for static data
  static: {
    staleTime: 1000 * 60 * 60, // 1 hour
    gcTime: 1000 * 60 * 60 * 24, // 24 hours
  },
  
  // Background refetch for user data
  background: {
    staleTime: DEFAULT_STALE_TIME,
    gcTime: DEFAULT_CACHE_TIME,
    refetchInterval: 1000 * 60 * 30, // 30 minutes
  },
} as const