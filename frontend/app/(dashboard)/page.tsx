'use client'

import { useState } from 'react'
import { Plus, BookOpen, TrendingUp, Clock, Star } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

import { BookForm } from '@/components/forms/book-form'
import { BookGrid } from '@/components/ui/book-grid'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { RecentActivity } from '@/components/dashboard/recent-activity'

import { useAuth } from '@/lib/auth/use-auth'
import { useBookStatistics, useRecentBooks } from '@/lib/queries/book-queries'
import { BookStatus } from '@/lib/types/book'

export default function DashboardPage() {
  const [showBookForm, setShowBookForm] = useState(false)
  const { user } = useAuth()
  
  const { data: stats, isLoading: statsLoading } = useBookStatistics()
  const { data: recentBooks, isLoading: booksLoading } = useRecentBooks(7, 6)

  const handleBookCreated = () => {
    setShowBookForm(false)
    // Queries will automatically refetch due to invalidation
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Olá, {user?.full_name || 'Usuário'}! 👋
          </h1>
          <p className="text-muted-foreground mt-2">
            Bem-vindo de volta à sua fábrica de livros mágicos
          </p>
        </div>
        
        <Button 
          onClick={() => setShowBookForm(true)}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Criar Livro
        </Button>
      </div>

      {/* Stats Cards */}
      <StatsCards stats={stats} isLoading={statsLoading} />

      {/* Main Content */}
      <Tabs defaultValue="recent" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="recent" className="gap-2">
            <Clock className="h-4 w-4" />
            Recentes
          </TabsTrigger>
          <TabsTrigger value="completed" className="gap-2">
            <BookOpen className="h-4 w-4" />
            Concluídos
          </TabsTrigger>
          <TabsTrigger value="activity" className="gap-2">
            <TrendingUp className="h-4 w-4" />
            Atividade
          </TabsTrigger>
          <TabsTrigger value="favorites" className="gap-2">
            <Star className="h-4 w-4" />
            Favoritos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="recent" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Livros Recentes</h2>
            <Button variant="outline" asChild>
              <a href="/dashboard/books">Ver todos</a>
            </Button>
          </div>
          
          {booksLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <Card key={i} className="animate-pulse">
                  <div className="aspect-[3/4] bg-muted rounded-t-lg" />
                  <CardContent className="p-4 space-y-2">
                    <div className="h-4 bg-muted rounded" />
                    <div className="h-3 bg-muted rounded w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <BookGrid books={recentBooks || []} />
          )}
        </TabsContent>

        <TabsContent value="completed" className="space-y-6">
          <BookGrid 
            books={recentBooks?.filter(book => book.status === BookStatus.COMPLETED) || []} 
            emptyMessage="Nenhum livro concluído ainda"
          />
        </TabsContent>

        <TabsContent value="activity" className="space-y-6">
          <RecentActivity />
        </TabsContent>

        <TabsContent value="favorites" className="space-y-6">
          <div className="text-center py-12">
            <Star className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Em breve!</h3>
            <p className="text-muted-foreground">
              A funcionalidade de favoritos será lançada em breve
            </p>
          </div>
        </TabsContent>
      </Tabs>

      {/* Book Creation Modal/Form */}
      {showBookForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-background rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <BookForm 
              onSuccess={handleBookCreated}
              onCancel={() => setShowBookForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}