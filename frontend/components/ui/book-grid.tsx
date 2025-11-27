'use client'

import { Book } from '@/lib/types/book'
import { BookCard } from '@/components/book-card'

interface BookGridProps {
  books: Book[]
  isLoading?: boolean
  emptyMessage?: string
  onBookClick?: (book: Book) => void
}

export function BookGrid({ 
  books, 
  isLoading = false, 
  emptyMessage = "Nenhum livro encontrado",
  onBookClick 
}: BookGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <BookCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (books.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
          <svg 
            className="w-12 h-12 text-muted-foreground"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={1.5} 
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2">
          {emptyMessage}
        </h3>
        <p className="text-muted-foreground mb-4">
          Comece criando seu primeiro livro personalizado
        </p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {books.map((book) => (
        <BookCard 
          key={book.id} 
          book={book} 
          onClick={() => onBookClick?.(book)}
        />
      ))}
    </div>
  )
}

function BookCardSkeleton() {
  return (
    <div className="bg-card rounded-lg border animate-pulse">
      <div className="aspect-[3/4] bg-muted rounded-t-lg" />
      <div className="p-4 space-y-3">
        <div className="h-5 bg-muted rounded" />
        <div className="h-4 bg-muted rounded w-2/3" />
        <div className="flex justify-between">
          <div className="h-4 bg-muted rounded w-16" />
          <div className="h-4 bg-muted rounded w-12" />
        </div>
      </div>
    </div>
  )
}