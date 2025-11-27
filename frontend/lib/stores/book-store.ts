'use client'

import { create } from 'zustand'
import { Book, BookStatus } from '../types/book'

interface BookState {
  selectedBook: Book | null
  recentBooks: Book[]
  bookCache: Record<number, Book>
  
  // Generation tracking
  generatingBooks: Set<number>
  generationProgress: Record<number, {
    taskId: string
    progress: number
    status: string
    message: string
  }>
  
  // Actions
  setSelectedBook: (book: Book | null) => void
  addToCache: (book: Book) => void
  removeFromCache: (bookId: number) => void
  updateBookInCache: (bookId: number, updates: Partial<Book>) => void
  setRecentBooks: (books: Book[]) => void
  
  // Generation actions
  startGeneration: (bookId: number, taskId: string) => void
  updateGeneration: (bookId: number, progress: number, status: string, message: string) => void
  completeGeneration: (bookId: number, book?: Book) => void
  clearGeneration: (bookId: number) => void
}

export const useBookStore = create<BookState>((set, get) => ({
  selectedBook: null,
  recentBooks: [],
  bookCache: {},
  generatingBooks: new Set(),
  generationProgress: {},

  setSelectedBook: (book: Book | null) => {
    set({ selectedBook: book })
    
    // Add to cache if not already there
    if (book && !get().bookCache[book.id]) {
      get().addToCache(book)
    }
  },

  addToCache: (book: Book) => {
    set(state => ({
      bookCache: {
        ...state.bookCache,
        [book.id]: book
      }
    }))
  },

  removeFromCache: (bookId: number) => {
    set(state => {
      const newCache = { ...state.bookCache }
      delete newCache[bookId]
      
      return {
        bookCache: newCache,
        selectedBook: state.selectedBook?.id === bookId ? null : state.selectedBook,
        recentBooks: state.recentBooks.filter(book => book.id !== bookId)
      }
    })
  },

  updateBookInCache: (bookId: number, updates: Partial<Book>) => {
    set(state => {
      const existingBook = state.bookCache[bookId]
      if (!existingBook) return state

      const updatedBook = { ...existingBook, ...updates }
      
      return {
        bookCache: {
          ...state.bookCache,
          [bookId]: updatedBook
        },
        selectedBook: state.selectedBook?.id === bookId ? updatedBook : state.selectedBook,
        recentBooks: state.recentBooks.map(book => 
          book.id === bookId ? updatedBook : book
        )
      }
    })
  },

  setRecentBooks: (books: Book[]) => {
    set({ recentBooks: books })
    
    // Add books to cache
    books.forEach(book => {
      get().addToCache(book)
    })
  },

  startGeneration: (bookId: number, taskId: string) => {
    set(state => ({
      generatingBooks: new Set([...state.generatingBooks, bookId]),
      generationProgress: {
        ...state.generationProgress,
        [bookId]: {
          taskId,
          progress: 0,
          status: 'pending',
          message: 'Iniciando geração...'
        }
      }
    }))

    // Update book status to processing if in cache
    get().updateBookInCache(bookId, { status: BookStatus.PROCESSING })
  },

  updateGeneration: (bookId: number, progress: number, status: string, message: string) => {
    set(state => {
      const currentProgress = state.generationProgress[bookId]
      if (!currentProgress) return state

      return {
        generationProgress: {
          ...state.generationProgress,
          [bookId]: {
            ...currentProgress,
            progress,
            status,
            message
          }
        }
      }
    })
  },

  completeGeneration: (bookId: number, book?: Book) => {
    set(state => {
      const newGeneratingBooks = new Set(state.generatingBooks)
      newGeneratingBooks.delete(bookId)

      const newProgress = { ...state.generationProgress }
      delete newProgress[bookId]

      return {
        generatingBooks: newGeneratingBooks,
        generationProgress: newProgress
      }
    })

    // Update book in cache if provided
    if (book) {
      get().addToCache(book)
    } else {
      // Just update status to completed
      get().updateBookInCache(bookId, { status: BookStatus.COMPLETED })
    }
  },

  clearGeneration: (bookId: number) => {
    set(state => {
      const newGeneratingBooks = new Set(state.generatingBooks)
      newGeneratingBooks.delete(bookId)

      const newProgress = { ...state.generationProgress }
      delete newProgress[bookId]

      return {
        generatingBooks: newGeneratingBooks,
        generationProgress: newProgress
      }
    })

    // Update book status to failed
    get().updateBookInCache(bookId, { status: BookStatus.FAILED })
  },
}))

// Computed selectors
export const useBookSelectors = () => {
  const store = useBookStore()
  
  return {
    ...store,
    
    // Computed values
    isGenerating: (bookId: number) => store.generatingBooks.has(bookId),
    getGenerationProgress: (bookId: number) => store.generationProgress[bookId] || null,
    getCachedBook: (bookId: number) => store.bookCache[bookId] || null,
    
    // Filtered books
    getBooksByStatus: (status: BookStatus) => 
      store.recentBooks.filter(book => book.status === status),
    
    getCompletedBooks: () => 
      store.recentBooks.filter(book => book.status === BookStatus.COMPLETED),
    
    getDraftBooks: () => 
      store.recentBooks.filter(book => book.status === BookStatus.DRAFT),
    
    getProcessingBooks: () => 
      store.recentBooks.filter(book => book.status === BookStatus.PROCESSING),
  }
}