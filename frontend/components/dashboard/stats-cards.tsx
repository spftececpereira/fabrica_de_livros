'use client'

import { BookOpen, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useBookStatistics } from '@/lib/queries/dashboard-queries' // Import the hook
import { BookStatistics } from '@/lib/types/book'

interface StatsCardsProps {
  // stats?: BookStatistics // No longer needed as prop
  // isLoading?: boolean // No longer needed as prop
}

export function StatsCards({ /* stats, isLoading */ }: StatsCardsProps) {
  const { data: stats, isLoading, isError } = useBookStatistics() // Use the hook

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 bg-muted rounded w-20" />
              <div className="h-4 w-4 bg-muted rounded" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted rounded w-16 mb-2" />
              <div className="h-3 bg-muted rounded w-24" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (isError || !stats) {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card className="col-span-4">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Erro</CardTitle>
                    <AlertCircle className="h-4 w-4 text-red-500" />
                </CardHeader>
                <CardContent>
                    <p className="text-xs text-muted-foreground">Não foi possível carregar as estatísticas.</p>
                </CardContent>
            </Card>
        </div>
    )
  }

  const cards = [
    {
      title: 'Total de Livros',
      value: stats.total_books || 0,
      description: 'Livros criados',
      icon: BookOpen,
      color: 'text-blue-600',
    },
    {
      title: 'Concluídos',
      value: stats.completed_books || 0,
      description: 'Prontos para download',
      icon: CheckCircle,
      color: 'text-green-600',
    },
    {
      title: 'Em Processamento',
      value: stats.processing_books || 0,
      description: 'Sendo gerados pela IA',
      icon: Clock,
      color: 'text-yellow-600',
    },
    {
      title: 'Rascunhos',
      value: stats.draft_books || 0,
      description: 'Aguardando geração',
      icon: AlertCircle,
      color: 'text-gray-600',
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {card.title}
            </CardTitle>
            <card.icon className={`h-4 w-4 ${card.color}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground">
              {card.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}