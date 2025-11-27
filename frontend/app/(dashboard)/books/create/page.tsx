'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import dynamic from 'next/dynamic'

import { Button } from '@/components/ui/button'
import { BookForm } from '@/components/forms/book-form'
import { useStartBookGeneration } from '@/lib/queries/book-queries'
import { Book } from '@/lib/types/book'

const BookGenerationProgress = dynamic(
  () => import('@/components/ui/book-generation-progress').then(mod => ({ default: mod.BookGenerationProgress })),
  {
    ssr: false,
    loading: () => <div className="text-center p-8">Carregando...</div>
  }
)


export default function CreateBookPage() {
  const router = useRouter()
  const [createdBook, setCreatedBook] = useState<Book | null>(null)
  const [showGeneration, setShowGeneration] = useState(false)
  
  const generateMutation = useStartBookGeneration()

  const handleBookCreated = async (book: Book) => {
    setCreatedBook(book)
    setShowGeneration(true)
    
    try {
      // Start generation process
      await generateMutation.mutateAsync(book.id)
    } catch (error) {
      console.error('Failed to start generation:', error)
      setShowGeneration(false)
    }
  }

  const handleGenerationComplete = () => {
    if (createdBook) {
      router.push(`/dashboard/books/${createdBook.id}`)
    }
  }

  const handleGenerationError = () => {
    setShowGeneration(false)
    // Book remains in draft state for user to try again
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </Button>
        
        <div>
          <h1 className="text-2xl font-bold">Criar Novo Livro</h1>
          <p className="text-muted-foreground">
            Preencha os detalhes e nossa IA criará seu livro personalizado
          </p>
        </div>
      </div>

      {/* Book Creation Form or Generation Progress */}
      {!showGeneration ? (
        <div className="max-w-2xl mx-auto">
          <BookForm 
            onSuccess={handleBookCreated}
            onCancel={() => router.back()}
          />
        </div>
      ) : (
        <div className="max-w-2xl mx-auto">
          {createdBook && (
            <BookGenerationProgress
              bookId={createdBook.id}
              bookTitle={createdBook.title}
              onComplete={handleGenerationComplete}
              onError={handleGenerationError}
            />
          )}
          
          {/* Additional info during generation */}
          <div className="mt-6 p-4 bg-muted/50 rounded-lg">
            <h3 className="font-semibold mb-2">Enquanto seu livro é criado...</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Nossa IA está analisando seus parâmetros</li>
              <li>• Gerando uma história única e envolvente</li>
              <li>• Criando ilustrações no estilo escolhido</li>
              <li>• Organizando tudo em um belo livro de colorir</li>
            </ul>
            
            <div className="mt-4 p-3 bg-background rounded border-l-4 border-l-blue-500">
              <p className="text-sm">
                💡 <strong>Dica:</strong> Você pode fechar esta página. Enviaremos uma notificação 
                quando seu livro estiver pronto!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Progress Steps Indicator */}
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-center space-x-4">
          <div className={`flex items-center ${!showGeneration ? 'text-primary' : 'text-muted-foreground'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              !showGeneration ? 'bg-primary text-primary-foreground' : 'bg-muted'
            }`}>
              1
            </div>
            <span className="ml-2 text-sm">Configuração</span>
          </div>
          
          <div className="flex-1 h-px bg-border mx-4" />
          
          <div className={`flex items-center ${showGeneration ? 'text-primary' : 'text-muted-foreground'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              showGeneration ? 'bg-primary text-primary-foreground' : 'bg-muted'
            }`}>
              2
            </div>
            <span className="ml-2 text-sm">Geração</span>
          </div>
          
          <div className="flex-1 h-px bg-border mx-4" />
          
          <div className="flex items-center text-muted-foreground">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold bg-muted">
              3
            </div>
            <span className="ml-2 text-sm">Concluído</span>
          </div>
        </div>
      </div>
    </div>
  )
}