'use client'

import { useQuery, useMutation, useInfiniteQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { api, downloadFile } from '../api'
import { queryKeys, invalidateQueries } from '../query-client'
import { useBookStore, useBookSelectors } from '../stores/book-store'
import { 
  Book, 
  BookCreate, 
  BookUpdate, 
  BookStatistics,
  BookGenerationStatus,
  BookFilters
} from '../types/book'
import { PaginatedResponse } from '../types/api'

// Get user's books with pagination and filters
export const useBooks = (filters?: BookFilters) => {
  return useInfiniteQuery({
    queryKey: queryKeys.books.list(filters),
    queryFn: async ({ pageParam = 0 }): Promise<PaginatedResponse<Book>> => {
      const params = new URLSearchParams({
        skip: pageParam.toString(),
        limit: (filters?.limit || 20).toString(),
        ...(filters?.status_filter && { status_filter: filters.status_filter }),
        ...(filters?.style_filter && { style_filter: filters.style_filter }),
        ...(filters?.search && { search: filters.search }),
        ...(filters?.sort_by && { sort_by: filters.sort_by }),
        ...(filters?.sort_order && { sort_order: filters.sort_order }),
      })
      
      return api.get<PaginatedResponse<Book>>(`/api/v1/books?${params.toString()}`)
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage) => {
      if (lastPage.has_next) {
        return lastPage.skip + lastPage.limit
      }
      return undefined
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  })
}

// Get single book details
export const useBook = (bookId: number) => {
  const { addToCache, getCachedBook } = useBookSelectors()
  
  return useQuery({
    queryKey: queryKeys.books.detail(bookId),
    queryFn: async (): Promise<Book> => {
      const book = await api.get<Book>(`/api/v1/books/${bookId}`)
      addToCache(book)
      return book
    },
    enabled: !!bookId,
    staleTime: 1000 * 60 * 5, // 5 minutes
    initialData: () => getCachedBook(bookId) || undefined,
  })
}

// Create book mutation
export const useCreateBook = () => {
  const { addToCache } = useBookSelectors()
  
  return useMutation({
    mutationFn: async (bookData: BookCreate): Promise<Book> => {
      return api.post<Book>('/api/v1/books', bookData)
    },
    onSuccess: (book) => {
      addToCache(book)
      invalidateQueries.books.lists()
      invalidateQueries.books.stats()
      toast.success('Livro criado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao criar livro')
    },
  })
}

// Update book mutation
export const useUpdateBook = (bookId: number) => {
  const { updateBookInCache } = useBookSelectors()
  
  return useMutation({
    mutationFn: async (updates: BookUpdate): Promise<Book> => {
      return api.put<Book>(`/api/v1/books/${bookId}`, updates)
    },
    onSuccess: (book) => {
      updateBookInCache(bookId, book)
      invalidateQueries.books.detail(bookId)
      invalidateQueries.books.lists()
      toast.success('Livro atualizado com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao atualizar livro')
    },
  })
}

// Delete book mutation
export const useDeleteBook = () => {
  const { removeFromCache } = useBookSelectors()
  
  return useMutation({
    mutationFn: async (bookId: number): Promise<void> => {
      return api.delete(`/api/v1/books/${bookId}`)
    },
    onSuccess: (_, bookId) => {
      removeFromCache(bookId)
      invalidateQueries.books.lists()
      invalidateQueries.books.stats()
      toast.success('Livro removido com sucesso!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao remover livro')
    },
  })
}

// Start book generation mutation
export const useStartBookGeneration = () => {
  const { startGeneration } = useBookSelectors()
  
  return useMutation({
    mutationFn: async (bookId: number): Promise<{ task_id: string }> => {
      return api.post<{ task_id: string }>(`/api/v1/books/${bookId}/generate`)
    },
    onSuccess: (data, bookId) => {
      startGeneration(bookId, data.task_id)
      toast.success('Geração do livro iniciada!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao iniciar geração do livro')
    },
  })
}

// Get book generation status
export const useBookGenerationStatus = (taskId: string, enabled: boolean = true) => {
  const { updateGeneration, completeGeneration, clearGeneration } = useBookSelectors()
  
  return useQuery({
    queryKey: queryKeys.books.generation.status(taskId),
    queryFn: async (): Promise<BookGenerationStatus> => {
      return api.get<BookGenerationStatus>(`/api/v1/books/generation-status/${taskId}`)
    },
    enabled: enabled && !!taskId,
    refetchInterval: (data) => {
      // Stop polling if generation is complete or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false
      }
      return 2000 // Poll every 2 seconds
    },
    onSuccess: (data) => {
      // Find book ID from generation progress
      const bookStore = useBookStore.getState()
      const bookId = Object.keys(bookStore.generationProgress).find(
        id => bookStore.generationProgress[parseInt(id)]?.taskId === taskId
      )
      
      if (bookId) {
        const bookIdNumber = parseInt(bookId)
        
        if (data.status === 'completed') {
          completeGeneration(bookIdNumber)
          invalidateQueries.books.detail(bookIdNumber)
          invalidateQueries.books.lists()
        } else if (data.status === 'failed') {
          clearGeneration(bookIdNumber)
          toast.error('Falha na geração do livro')
        } else {
          updateGeneration(bookIdNumber, data.progress, data.status, data.message)
        }
      }
    },
  })
}

// Generate PDF mutation
export const useGeneratePDF = () => {
  return useMutation({
    mutationFn: async (bookId: number): Promise<{ task_id: string }> => {
      return api.post<{ task_id: string }>(`/api/v1/books/${bookId}/generate-pdf`)
    },
    onSuccess: () => {
      toast.success('Geração do PDF iniciada!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao gerar PDF')
    },
  })
}

// Download book PDF
export const useDownloadPDF = () => {
  return useMutation({
    mutationFn: async ({ bookId, filename }: { bookId: number; filename?: string }) => {
      return downloadFile(`/api/v1/books/${bookId}/pdf`, filename)
    },
    onSuccess: () => {
      toast.success('Download iniciado!')
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao baixar PDF')
    },
  })
}

// Get book statistics
export const useBookStatistics = () => {
  return useQuery({
    queryKey: queryKeys.books.stats(),
    queryFn: async (): Promise<BookStatistics> => {
      return api.get<BookStatistics>('/api/v1/books/stats/overview')
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

// Get recent books
export const useRecentBooks = (days: number = 7, limit: number = 10) => {
  const setRecentBooks = useBookStore(state => state.setRecentBooks)
  
  return useQuery({
    queryKey: queryKeys.books.recent(),
    queryFn: async (): Promise<Book[]> => {
      const params = new URLSearchParams({
        days: days.toString(),
        limit: limit.toString(),
      })
      
      return api.get<Book[]>(`/api/v1/books/recent/list?${params.toString()}`)
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    onSuccess: (books) => {
      setRecentBooks(books)
    },
  })
}

// Search books
export const useSearchBooks = (searchTerm: string, limit: number = 50) => {
  return useQuery({
    queryKey: queryKeys.books.search(searchTerm),
    queryFn: async (): Promise<Book[]> => {
      const params = new URLSearchParams({
        limit: limit.toString(),
      })
      
      return api.get<Book[]>(`/api/v1/books/search/${encodeURIComponent(searchTerm)}?${params.toString()}`)
    },
    enabled: searchTerm.length >= 2, // Only search if term has 2+ characters
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Custom hook for book management
export const useBookManagement = () => {
  const bookStore = useBookSelectors()
  const createMutation = useCreateBook()
  const deleteMutation = useDeleteBook()
  const generateMutation = useStartBookGeneration()
  const pdfMutation = useGeneratePDF()
  const downloadMutation = useDownloadPDF()
  
  return {
    // Store state
    ...bookStore,
    
    // Actions
    createBook: createMutation.mutateAsync,
    deleteBook: deleteMutation.mutateAsync,
    generateBook: generateMutation.mutateAsync,
    generatePDF: pdfMutation.mutateAsync,
    downloadPDF: downloadMutation.mutateAsync,
    
    // Loading states
    isCreating: createMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isGenerating: generateMutation.isPending,
    isGeneratingPDF: pdfMutation.isPending,
    isDownloading: downloadMutation.isPending,
  }
}