'use client'

import { useState } from 'react'
import { Plus, Search, Filter, SortAsc } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

import { BookGrid } from '@/components/ui/book-grid'
import { BookGenerationNotification } from '@/components/ui/book-generation-progress'
import { useBooks } from '@/lib/queries/book-queries'
import { BookStatus, BookStyle, bookHelpers } from '@/lib/types/book'
import { useWebSocket } from '@/hooks/use-websocket'

export default function BooksPage() {
  const [activeTab, setActiveTab] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'created_at' | 'title' | 'updated_at'>('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [styleFilter, setStyleFilter] = useState<BookStyle | ''>('')
  
  const { isConnected } = useWebSocket()

  // Build filters based on current tab and controls
  const filters = {
    search: searchTerm || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    style_filter: styleFilter || undefined,
    status_filter: activeTab === 'all' ? undefined : activeTab,
    limit: 20,
  }

  const { 
    data, 
    isLoading, 
    fetchNextPage, 
    hasNextPage, 
    isFetchingNextPage 
  } = useBooks(filters)

  // Flatten paginated data
  const books = data?.pages.flatMap(page => page.items) || []
  const totalBooks = data?.pages[0]?.total || 0

  const handleLoadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      fetchNextPage()
    }
  }

  const getTabCount = (status: string) => {
    if (!data?.pages[0]) return 0
    
    // This is a simplified count - in a real app you'd get these from the API
    switch (status) {
      case 'draft': return books.filter(b => b.status === BookStatus.DRAFT).length
      case 'processing': return books.filter(b => b.status === BookStatus.PROCESSING).length
      case 'completed': return books.filter(b => b.status === BookStatus.COMPLETED).length
      case 'failed': return books.filter(b => b.status === BookStatus.FAILED).length
      default: return totalBooks
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Meus Livros</h1>
          <p className="text-muted-foreground">
            Gerencie sua biblioteca de livros personalizados
            {!isConnected && (
              <span className="text-amber-600 ml-2">
                • Atualizações em tempo real indisponíveis
              </span>
            )}
          </p>
        </div>
        
        <Button asChild>
          <Link href="/dashboard/books/create">
            <Plus className="h-4 w-4 mr-2" />
            Criar Livro
          </Link>
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filtros</CardTitle>
          <CardDescription>
            Encontre seus livros rapidamente
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Pesquisar livros por título..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filters Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Select value={styleFilter} onValueChange={(value: BookStyle | '') => setStyleFilter(value)}>
              <SelectTrigger>
                <SelectValue placeholder="Todos os estilos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos os estilos</SelectItem>
                {Object.values(BookStyle).map(style => (
                  <SelectItem key={style} value={style}>
                    {bookHelpers.getStyleLabel(style)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at">Data de criação</SelectItem>
                <SelectItem value="updated_at">Última modificação</SelectItem>
                <SelectItem value="title">Título</SelectItem>
              </SelectContent>
            </Select>

            <Select value={sortOrder} onValueChange={(value: any) => setSortOrder(value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Mais recente</SelectItem>
                <SelectItem value="asc">Mais antigo</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Books List with Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all" className="gap-2">
            Todos
            <span className="bg-muted text-muted-foreground px-2 py-1 rounded-full text-xs">
              {getTabCount('all')}
            </span>
          </TabsTrigger>
          <TabsTrigger value="draft" className="gap-2">
            Rascunhos
            <span className="bg-muted text-muted-foreground px-2 py-1 rounded-full text-xs">
              {getTabCount('draft')}
            </span>
          </TabsTrigger>
          <TabsTrigger value="processing" className="gap-2">
            Processando
            <span className="bg-muted text-muted-foreground px-2 py-1 rounded-full text-xs">
              {getTabCount('processing')}
            </span>
          </TabsTrigger>
          <TabsTrigger value="completed" className="gap-2">
            Concluídos
            <span className="bg-muted text-muted-foreground px-2 py-1 rounded-full text-xs">
              {getTabCount('completed')}
            </span>
          </TabsTrigger>
          <TabsTrigger value="failed" className="gap-2">
            Com erro
            <span className="bg-muted text-muted-foreground px-2 py-1 rounded-full text-xs">
              {getTabCount('failed')}
            </span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="space-y-6">
          <BookGrid 
            books={books}
            isLoading={isLoading}
            emptyMessage={
              activeTab === 'all' ? "Nenhum livro encontrado. Que tal criar seu primeiro livro?" :
              activeTab === 'draft' ? "Nenhum rascunho encontrado" :
              activeTab === 'processing' ? "Nenhum livro sendo processado" :
              activeTab === 'completed' ? "Nenhum livro concluído ainda" :
              "Nenhum livro com erro"
            }
          />

          {/* Load More Button */}
          {hasNextPage && (
            <div className="text-center">
              <Button 
                onClick={handleLoadMore}
                disabled={isFetchingNextPage}
                variant="outline"
              >
                {isFetchingNextPage ? (
                  <>
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Carregando...
                  </>
                ) : (
                  'Carregar mais livros'
                )}
              </Button>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}