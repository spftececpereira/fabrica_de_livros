import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { BookStatistics } from '@/lib/types/book' // Assuming this type exists

interface ActivityItem {
  id: string
  type: 'book_created' | 'book_completed' | 'pdf_downloaded' | 'book_favorited' | string
  title: string
  description: string
  timestamp: string // Changed to string to match backend mock
  metadata?: any
}

// Fetch user's recent activity
export function useUserActivity() {
  return useQuery<ActivityItem[], Error>({
    queryKey: ['userActivity'],
    queryFn: () => api.get<ActivityItem[]>('/api/v1/users/me/activity'),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Fetch book statistics
export function useBookStatistics() {
  return useQuery<BookStatistics, Error>({
    queryKey: ['bookStatistics'],
    queryFn: () => api.get<BookStatistics>('/api/v1/books/stats/overview'), // Assuming this endpoint exists for books
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Fetch user statistics (might be more for admin)
export function useUserStatistics() {
  return useQuery<any, Error>({
    queryKey: ['userStatistics'],
    queryFn: () => api.get<any>('/api/v1/users/stats/overview'),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}
