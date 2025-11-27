'use client'

import { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, Download, ArrowLeft, Maximize, Minimize } from 'lucide-react'
import Image from 'next/image'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

import { Book, Page } from '@/lib/types/book'
import { useDownloadPDF } from '@/lib/queries/book-queries'

interface BookReaderProps {
  book: Book
  onClose?: () => void
}

export function BookReader({ book, onClose }: BookReaderProps) {
  const [currentPage, setCurrentPage] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const downloadMutation = useDownloadPDF()

  const pages = book.pages.sort((a, b) => a.page_number - b.page_number)
  const totalPages = pages.length
  const progress = totalPages > 0 ? ((currentPage + 1) / totalPages) * 100 : 0

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft' && currentPage > 0) {
        setCurrentPage(prev => prev - 1)
      } else if (e.key === 'ArrowRight' && currentPage < totalPages - 1) {
        setCurrentPage(prev => prev + 1)
      } else if (e.key === 'Escape') {
        if (isFullscreen) {
          setIsFullscreen(false)
        } else {
          onClose?.()
        }
      }
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', handleKeyPress)
      return () => window.removeEventListener('keydown', handleKeyPress)
    }
  }, [currentPage, totalPages, isFullscreen, onClose])

  const handleDownload = async () => {
    try {
      await downloadMutation.mutateAsync({
        bookId: book.id,
        filename: `${book.title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`
      })
    } catch (error) {
      // Error is handled by the mutation
    }
  }

  const nextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(prev => prev + 1)
    }
  }

  const prevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(prev => prev - 1)
    }
  }

  if (totalPages === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-6xl mb-4">📖</div>
          <h3 className="text-lg font-semibold mb-2">Livro sem páginas</h3>
          <p className="text-muted-foreground">
            Este livro ainda não possui páginas geradas.
          </p>
        </div>
      </div>
    )
  }

  const currentPageData = pages[currentPage]

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-background' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-4">
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar
            </Button>
          )}
          
          <div>
            <h1 className="text-xl font-bold">{book.title}</h1>
            <p className="text-sm text-muted-foreground">
              Página {currentPage + 1} de {totalPages}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            {isFullscreen ? (
              <Minimize className="h-4 w-4" />
            ) : (
              <Maximize className="h-4 w-4" />
            )}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownload}
            disabled={downloadMutation.isPending}
          >
            <Download className="h-4 w-4 mr-2" />
            {downloadMutation.isPending ? 'Baixando...' : 'PDF'}
          </Button>
        </div>
      </div>

      {/* Progress */}
      <div className="px-4 py-2">
        <Progress value={progress} className="w-full" />
      </div>

      {/* Reader */}
      <div className="flex-1 flex">
        {/* Navigation - Previous */}
        <div className="w-16 flex items-center justify-center">
          <Button
            variant="ghost"
            size="lg"
            onClick={prevPage}
            disabled={currentPage === 0}
            className="h-20 w-12"
          >
            <ChevronLeft className="h-8 w-8" />
          </Button>
        </div>

        {/* Page Content */}
        <div className="flex-1 max-w-4xl mx-auto p-4">
          <Card className="h-full">
            <CardContent className="p-0 h-full">
              <div className="grid md:grid-cols-2 h-full">
                {/* Image Side */}
                <div className="relative bg-muted rounded-l-lg overflow-hidden">
                  {currentPageData.image_url ? (
                    <Image
                      src={currentPageData.image_url}
                      alt={`Página ${currentPageData.page_number}`}
                      fill
                      className="object-cover"
                      priority
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center text-muted-foreground">
                        <div className="text-4xl mb-4">🎨</div>
                        <p>Imagem sendo gerada...</p>
                        {currentPageData.image_prompt && (
                          <p className="text-xs mt-2 max-w-xs">
                            Prompt: {currentPageData.image_prompt}
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="absolute top-4 left-4">
                    <Badge variant="secondary">
                      Página {currentPageData.page_number}
                    </Badge>
                  </div>
                </div>

                {/* Text Side */}
                <div className="p-8 flex flex-col justify-center">
                  {currentPageData.text_content ? (
                    <div className="prose prose-lg dark:prose-invert max-w-none">
                      <p className="text-lg leading-relaxed whitespace-pre-wrap">
                        {currentPageData.text_content}
                      </p>
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground">
                      <div className="text-4xl mb-4">✍️</div>
                      <p>Texto sendo gerado...</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Navigation - Next */}
        <div className="w-16 flex items-center justify-center">
          <Button
            variant="ghost"
            size="lg"
            onClick={nextPage}
            disabled={currentPage === totalPages - 1}
            className="h-20 w-12"
          >
            <ChevronRight className="h-8 w-8" />
          </Button>
        </div>
      </div>

      {/* Footer Controls */}
      <div className="flex items-center justify-center gap-2 p-4 border-t">
        <Button
          variant="outline"
          size="sm"
          onClick={prevPage}
          disabled={currentPage === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Anterior
        </Button>

        <div className="flex gap-1">
          {pages.map((_, index) => (
            <Button
              key={index}
              variant={index === currentPage ? "default" : "outline"}
              size="sm"
              onClick={() => setCurrentPage(index)}
              className="w-8 h-8 p-0"
            >
              {index + 1}
            </Button>
          ))}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={nextPage}
          disabled={currentPage === totalPages - 1}
        >
          Próxima
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>

      {/* Keyboard shortcuts help */}
      <div className="text-xs text-muted-foreground text-center pb-2">
        Use as setas ← → para navegar • ESC para {isFullscreen ? 'sair do tela cheia' : 'fechar'}
      </div>
    </div>
  )
}