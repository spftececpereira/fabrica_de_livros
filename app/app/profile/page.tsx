"use client"

import { useEffect, useState } from "react"
import { AppHeader } from "@/components/app-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Loader2, Trophy, BookOpen, Palette, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useAuthContext } from "@/components/auth-provider"
import type { Book, UserBadge } from "@/lib/types"

export default function ProfilePage() {
  const { user, loading: authLoading } = useAuthContext()
  const [books, setBooks] = useState<Book[]>([])
  const [badges, setBadges] = useState<UserBadge[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && user) {
      fetchData()
    }
  }, [authLoading, user])

  const fetchData = async () => {
    try {
      const [booksRes, badgesRes] = await Promise.all([fetch("/api/books"), fetch("/api/badges")])

      if (booksRes.ok) {
        const booksData = await booksRes.json()
        setBooks(booksData)
      }

      if (badgesRes.ok) {
        const badgesData = await badgesRes.json()
        setBadges(badgesData)
      }
    } catch (error) {
      console.error("Error fetching data:", error)
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

  const getUserInitials = () => {
    if (!user?.user_metadata?.name) return "U"
    const names = user.user_metadata.name.split(" ")
    return names.length > 1 ? `${names[0][0]}${names[1][0]}` : names[0][0]
  }

  const completedBooks = books.filter((b) => b.status === "completed").length
  const totalPages = books.reduce((sum, b) => sum + (b.status === "completed" ? b.pages_count : 0), 0)
  const stylesUsed = new Set(books.map((b) => b.style)).size

  return (
    <div className="min-h-screen bg-background">
      <AppHeader />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/app">
            <Button variant="ghost" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Voltar para Biblioteca
            </Button>
          </Link>
        </div>

        <div className="mx-auto max-w-4xl space-y-6">
          {/* Profile Header */}
          <Card>
            <CardContent className="flex flex-col items-center gap-4 py-8 md:flex-row md:items-start">
              <Avatar className="h-24 w-24">
                <AvatarImage
                  src={user?.user_metadata?.avatar_url || "/placeholder.svg"}
                  alt={user?.user_metadata?.name || "User"}
                />
                <AvatarFallback className="bg-primary text-2xl text-primary-foreground">
                  {getUserInitials()}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 text-center md:text-left">
                <h1 className="text-2xl font-bold">{user?.user_metadata?.name || "Usuário"}</h1>
                <p className="text-muted-foreground">{user?.email}</p>

                <div className="mt-4 flex flex-wrap justify-center gap-6 md:justify-start">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{completedBooks}</div>
                    <div className="text-sm text-muted-foreground">Livros Criados</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-accent">{totalPages}</div>
                    <div className="text-sm text-muted-foreground">Páginas Geradas</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-chart-3">{badges.length}</div>
                    <div className="text-sm text-muted-foreground">Conquistas</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Statistics */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total de Livros</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{books.length}</div>
                <p className="text-xs text-muted-foreground">{completedBooks} concluídos</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Estilos Explorados</CardTitle>
                <Palette className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stylesUsed}/4</div>
                <p className="text-xs text-muted-foreground">Estilos artísticos</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Conquistas</CardTitle>
                <Trophy className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{badges.length}</div>
                <p className="text-xs text-muted-foreground">Badges desbloqueadas</p>
              </CardContent>
            </Card>
          </div>

          {/* Badges */}
          <Card>
            <CardHeader>
              <CardTitle>Minhas Conquistas</CardTitle>
              <CardDescription>Badges que você conquistou criando livros incríveis</CardDescription>
            </CardHeader>
            <CardContent>
              {badges.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">
                  <Trophy className="mx-auto mb-2 h-12 w-12 opacity-20" />
                  <p>Nenhuma conquista ainda. Crie seu primeiro livro para começar!</p>
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {badges.map((userBadge) => (
                    <div key={userBadge.id} className="flex items-start gap-3 rounded-lg border bg-card p-4">
                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10">
                        <Trophy className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold">{userBadge.badge?.name}</h3>
                        <p className="text-sm text-muted-foreground">{userBadge.badge?.description}</p>
                        <Badge variant="outline" className="mt-2 text-xs">
                          {new Date(userBadge.earned_at).toLocaleDateString("pt-BR")}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
