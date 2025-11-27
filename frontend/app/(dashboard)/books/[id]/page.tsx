'use client'

import { useParams, useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'

import { BookReader } from '@/components/ui/book-reader'
import { useBook } from '@/lib/queries/book-queries'

export default function BookReaderPage() {
  const params = useParams()
  const router = useRouter()
  const bookId = parseInt(params.id as string)

  const { data: book, isLoading, error } = useBook(bookId)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Carregando livro...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-6xl mb-4">😞</div>
          <h3 className="text-lg font-semibold mb-2">Erro ao carregar livro</h3>
          <p className="text-muted-foreground mb-4">
            {error.message || 'Não foi possível carregar o livro.'}
          </p>
          <button
            onClick={() => router.back()}
            className="text-primary hover:underline"
          >
            Voltar
          </button>
        </div>
      </div>
    )
  }

  if (!book) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-6xl mb-4">📖</div>
          <h3 className="text-lg font-semibold mb-2">Livro não encontrado</h3>
          <p className="text-muted-foreground mb-4">
            O livro que você está procurando não existe ou foi removido.
          </p>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-primary hover:underline"
          >
            Ir para Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen -m-6">
      <BookReader 
        book={book} 
        onClose={() => router.back()} 
      />
    </div>
  )
}