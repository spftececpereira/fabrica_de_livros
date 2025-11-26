"use client"

import { useEffect, useState } from "react"
import { AppHeader } from "@/components/app-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, BookOpen, Loader2, Search, Filter } from "lucide-react"
import Link from "next/link"
import { useAuthContext } from "@/components/auth-provider"
import type { Book } from "@/lib/types"

export default function AppPage() {
  const { user, loading: authLoading } = useAuthContext()
  const [books, setBooks] = useState<Book[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterStyle, setFilterStyle] = useState<string>("all")
  const [filterStatus, setFilterStatus] = useState<string>("all")

  useEffect(() => {
    if (!authLoading && user) {
      fetchBooks()
    }
  }, [authLoading, user])

  const fetchBooks = async () => {
    try {
      const response = await fetch("/api/books")
      if (!response.ok) throw new Error("Failed to fetch books")
      const data = await response.json()
      setBooks(data)
    } catch (error) {
      console.error("Error fetching books:", error)
    } finally {
      setLoading(false)
    }
  }

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  // Filter books
  const filteredBooks = books.filter((book) => {
    const matchesSearch =
      book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      book.theme.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStyle = filterStyle === "all" || book.style === filterStyle
    const matchesStatus = filterStatus === "all" || book.status === filterStatus
    return matchesSearch && matchesStyle && matchesStatus
  })

  const statusColors = {
    generating: "bg-yellow-500",
    completed: "bg-green-500",
    failed: "bg-red-500",
  }

  const statusLabels = {
    generating: "Gerando",
    completed: "Concluído",
    failed: "Falhou",
  }

  const styleLabels = {
    cartoon: "Cartoon",
    manga: "Mangá",
    realistic: "Realista",
    classic: "Clássico",
  }

  return (
    <div className="min-h-screen bg-background">
      <AppHeader />

      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Minha Biblioteca</h1>
            <p className="text-muted-foreground">
              {books.length} {books.length === 1 ? "livro criado" : "livros criados"}
            </p>
          </div>
          <Link href="/app/create">
            <Button size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              Criar Novo Livro
            </Button>
          </Link>
        </div>

        {books.length === 0 ? (
          /* Empty state */
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
                <BookOpen className="h-10 w-10 text-primary" />
              </div>
              <h2 className="mb-2 text-2xl font-bold">Nenhum livro criado ainda</h2>
              <p className="mb-6 text-center text-muted-foreground">
                Comece criando seu primeiro livro de colorir personalizado
              </p>
              <Link href="/app/create">
                <Button size="lg" className="gap-2">
                  <Plus className="h-5 w-5" />
                  Criar Meu Primeiro Livro
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Filters */}
            <div className="mb-6 flex flex-col gap-4 md:flex-row">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar por título ou tema..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              <div className="flex gap-2">
                <Select value={filterStyle} onValueChange={setFilterStyle}>
                  <SelectTrigger className="w-[180px] bg-transparent">
                    <Filter className="mr-2 h-4 w-4" />
                    <SelectValue placeholder="Estilo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os estilos</SelectItem>
                    <SelectItem value="cartoon">Cartoon</SelectItem>
                    <SelectItem value="manga">Mangá</SelectItem>
                    <SelectItem value="realistic">Realista</SelectItem>
                    <SelectItem value="classic">Clássico</SelectItem>
                  </SelectContent>
                </Select>

                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger className="w-[180px] bg-transparent">
                    <Filter className="mr-2 h-4 w-4" />
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os status</SelectItem>
                    <SelectItem value="completed">Concluído</SelectItem>
                    <SelectItem value="generating">Gerando</SelectItem>
                    <SelectItem value="failed">Falhou</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Books Grid */}
            {filteredBooks.length === 0 ? (
              <Card className="border-dashed">
                <CardContent className="py-12 text-center">
                  <p className="text-muted-foreground">Nenhum livro encontrado com os filtros selecionados</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {filteredBooks.map((book) => (
                  <Link key={book.id} href={`/app/books/${book.id}`}>
                    <Card className="group h-full transition-all hover:shadow-lg">
                      <CardContent className="p-4">
                        {/* Thumbnail */}
                        <div className="mb-3 aspect-[3/4] overflow-hidden rounded-lg bg-gradient-to-br from-primary/10 to-accent/10">
                          {book.cover_image_url ? (
                            <img
                              src={book.cover_image_url}
                              alt={`Capa de ${book.title}`}
                              className="h-full w-full object-cover"
                              onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.onerror = null; // Evita loop infinito se a imagem fallback também falhar
                                target.style.display = 'none';
                                const fallbackDiv = target.parentElement?.querySelector('div');
                                if (fallbackDiv) fallbackDiv.style.display = 'flex';
                              }}
                            />
                          ) : (
                            <div className="flex h-full items-center justify-center">
                              <BookOpen className="h-16 w-16 text-primary/40 transition-transform group-hover:scale-110" />
                            </div>
                          )}
                        </div>

                        {/* Book Info */}
                        <div className="space-y-2">
                          <div className="flex items-start justify-between gap-2">
                            <h3 className="font-semibold leading-tight line-clamp-2">{book.title}</h3>
                            <Badge className={`${statusColors[book.status]} shrink-0 text-xs`}>
                              {statusLabels[book.status]}
                            </Badge>
                          </div>

                          <p className="text-sm text-muted-foreground line-clamp-2">{book.theme}</p>

                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <span>{styleLabels[book.style]}</span>
                            <span>{book.pages_count} páginas</span>
                          </div>

                          {book.has_story && (
                            <Badge variant="outline" className="text-xs">
                              Com história
                            </Badge>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
