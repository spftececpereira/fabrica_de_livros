export enum BookStatus {
  DRAFT = "draft",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}

export enum BookStyle {
  CARTOON = "cartoon",
  REALISTIC = "realistic",
  MANGA = "manga",
  CLASSIC = "classic",
}

export interface Book {
  id: number
  title: string
  description: string | null
  pages_count: number
  style: BookStyle
  status: BookStatus
  cover_image: string | null
  pdf_file: string | null
  user_id: number
  created_at: string
  updated_at: string | null
  pages: Page[]
}

export interface Page {
  id: number
  book_id: number
  page_number: number
  text_content: string | null
  image_url: string | null
  image_prompt: string | null
  created_at: string
  updated_at: string | null
}

export interface BookCreate {
  title: string
  description?: string
  pages_count: number
  style: BookStyle
}

export interface BookUpdate {
  title?: string
  description?: string
  pages_count?: number
  style?: BookStyle
}

export interface BookGenerationStatus {
  task_id: string
  status: "pending" | "processing" | "completed" | "failed"
  progress: number
  message: string
  current_step?: string
  estimated_completion?: string
}

export interface BookStatistics {
  total_books: number
  completed_books: number
  draft_books: number
  processing_books: number
  failed_books: number
  total_pages: number
  books_by_style: Record<BookStyle, number>
  recent_activity: {
    books_created_this_week: number
    books_completed_this_week: number
  }
}

// Validation constants (must match backend)
export const BOOK_CONSTRAINTS = {
  MIN_PAGES: 5,
  MAX_PAGES: 20,
  MIN_TITLE_LENGTH: 3,
  MAX_TITLE_LENGTH: 200,
  MAX_DESCRIPTION_LENGTH: 1000,
  VALID_STYLES: Object.values(BookStyle),
  VALID_STATUSES: Object.values(BookStatus),
} as const

// Helper functions
export const bookHelpers = {
  isEditable: (book: Book): boolean => 
    [BookStatus.DRAFT, BookStatus.FAILED].includes(book.status),
  
  isProcessing: (book: Book): boolean => 
    book.status === BookStatus.PROCESSING,
  
  isCompleted: (book: Book): boolean => 
    book.status === BookStatus.COMPLETED,
  
  canGeneratePdf: (book: Book): boolean => 
    book.status === BookStatus.COMPLETED && book.pages.length === book.pages_count,
  
  getStyleLabel: (style: BookStyle): string => {
    const labels = {
      [BookStyle.CARTOON]: "Cartoon",
      [BookStyle.REALISTIC]: "Realista",
      [BookStyle.MANGA]: "Mangá",
      [BookStyle.CLASSIC]: "Clássico",
    }
    return labels[style] || style
  },
  
  getStatusLabel: (status: BookStatus): string => {
    const labels = {
      [BookStatus.DRAFT]: "Rascunho",
      [BookStatus.PROCESSING]: "Processando",
      [BookStatus.COMPLETED]: "Concluído",
      [BookStatus.FAILED]: "Falhou",
    }
    return labels[status] || status
  },
  
  getStatusColor: (status: BookStatus): string => {
    const colors = {
      [BookStatus.DRAFT]: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
      [BookStatus.PROCESSING]: "bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-300",
      [BookStatus.COMPLETED]: "bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-300",
      [BookStatus.FAILED]: "bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-300",
    }
    return colors[status] || colors[BookStatus.DRAFT]
  }
}