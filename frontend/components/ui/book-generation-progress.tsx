'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useBookGenerationUpdates } from '@/hooks/use-websocket'

interface BookGenerationProgressProps {
  bookId: number
  bookTitle: string
  initialTaskId?: string
  onComplete?: () => void
  onError?: () => void
}

export function BookGenerationProgress({
  bookId,
  bookTitle,
  initialTaskId,
  onComplete,
  onError
}: BookGenerationProgressProps) {
  const router = useRouter()
  const generationStatus = useBookGenerationUpdates(bookId)
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    if (generationStatus.status === 'completed') {
      setTimeout(() => {
        onComplete?.()
        setIsVisible(false)
      }, 3000) // Show success for 3 seconds
    } else if (generationStatus.status === 'failed') {
      onError?.()
    }
  }, [generationStatus.status, onComplete, onError])

  if (!isVisible) {
    return null
  }

  const getStatusInfo = () => {
    switch (generationStatus.status) {
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bgColor: 'bg-green-100 dark:bg-green-900',
          title: 'Geração Concluída! 🎉',
          description: 'Seu livro está pronto para visualização'
        }
      case 'failed':
        return {
          icon: XCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-100 dark:bg-red-900',
          title: 'Erro na Geração',
          description: 'Houve um problema ao gerar seu livro'
        }
      case 'processing':
      default:
        return {
          icon: Loader2,
          color: 'text-blue-600',
          bgColor: 'bg-blue-100 dark:bg-blue-900',
          title: 'Gerando seu livro...',
          description: 'Nossa IA está criando seu conteúdo personalizado'
        }
    }
  }

  const statusInfo = getStatusInfo()
  const Icon = statusInfo.icon
  const progress = generationStatus.progress || 0

  return (
    <Card className={`${statusInfo.bgColor} border-l-4 ${
      generationStatus.status === 'completed' ? 'border-l-green-500' :
      generationStatus.status === 'failed' ? 'border-l-red-500' :
      'border-l-blue-500'
    }`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Icon 
              className={`h-6 w-6 ${statusInfo.color} ${
                generationStatus.status === 'processing' ? 'animate-spin' : ''
              }`} 
            />
            <div>
              <CardTitle className="text-lg">{statusInfo.title}</CardTitle>
              <CardDescription className="text-sm">
                {statusInfo.description}
              </CardDescription>
            </div>
          </div>
          
          <Badge variant={
            generationStatus.status === 'completed' ? 'default' :
            generationStatus.status === 'failed' ? 'destructive' :
            'secondary'
          }>
            {generationStatus.status === 'completed' ? 'Concluído' :
             generationStatus.status === 'failed' ? 'Falhou' :
             'Processando'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Book Info */}
        <div className="p-3 bg-background/50 rounded-lg">
          <h3 className="font-semibold text-sm mb-1">{bookTitle}</h3>
          <p className="text-xs text-muted-foreground">
            {generationStatus.taskId && `ID da tarefa: ${generationStatus.taskId}`}
          </p>
        </div>

        {/* Progress Bar */}
        {generationStatus.status !== 'failed' && (
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Progresso</span>
              <span className="text-sm text-muted-foreground">{progress}%</span>
            </div>
            <Progress 
              value={progress} 
              className="h-2"
            />
          </div>
        )}

        {/* Current Step */}
        {generationStatus.currentStep && (
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              {generationStatus.currentStep}
            </span>
          </div>
        )}

        {/* Status Message */}
        {generationStatus.message && (
          <div className="p-2 bg-background/30 rounded text-sm">
            {generationStatus.message}
          </div>
        )}

        {/* Estimated Time (if processing) */}
        {generationStatus.status === 'processing' && (
          <div className="text-xs text-muted-foreground text-center">
            Tempo estimado: 2-5 minutos
          </div>
        )}

        {/* Action Buttons */}
        {generationStatus.status === 'completed' && (
          <div className="flex gap-2 pt-2">
            <Button 
              size="sm" 
              onClick={() => router.push(`/dashboard/books/${bookId}`)}
              className="flex-1"
            >
              Ver Livro
            </Button>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={() => setIsVisible(false)}
            >
              Fechar
            </Button>
          </div>
        )}

        {generationStatus.status === 'failed' && (
          <div className="flex gap-2 pt-2">
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => router.refresh()}
              className="flex-1"
            >
              Tentar Novamente
            </Button>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={() => setIsVisible(false)}
            >
              Fechar
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Minimal version for notifications
export function BookGenerationNotification({
  bookId,
  bookTitle,
  status,
  progress = 0,
  message
}: {
  bookId: number
  bookTitle: string
  status: 'processing' | 'completed' | 'failed'
  progress?: number
  message?: string
}) {
  const router = useRouter()
  const getStatusIcon = () => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'failed': return <XCircle className="h-5 w-5 text-red-600" />
      default: return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
    }
  }

  return (
    <div className="flex items-start gap-3 p-3 bg-background border rounded-lg">
      {getStatusIcon()}
      
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-medium truncate">{bookTitle}</h4>
        <p className="text-xs text-muted-foreground">
          {message || `Status: ${status}`}
        </p>
        
        {status === 'processing' && (
          <div className="mt-2">
            <div className="flex justify-between text-xs mb-1">
              <span>Progresso</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-1" />
          </div>
        )}
      </div>
      
      {status === 'completed' && (
        <Button 
          size="sm" 
          variant="outline"
          onClick={() => router.push(`/dashboard/books/${bookId}`)}
        >
          Ver
        </Button>
      )}
    </div>
  )
}