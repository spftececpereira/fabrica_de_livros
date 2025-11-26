"use client"

import { useEffect, useState } from "react"
import { AppHeader } from "@/components/app-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Loader2, Trophy, Lock, ArrowLeft, Sparkles } from "lucide-react"
import Link from "next/link"
import { useAuthContext } from "@/components/auth-provider"
import type { Badge as BadgeType, UserBadge, Book } from "@/lib/types"

interface BadgeWithProgress extends BadgeType {
  earned: boolean
  earnedAt?: string
  progress: number
  total: number
  description_progress?: string
}

export default function AchievementsPage() {
  const { user, loading: authLoading } = useAuthContext()
  const [badges, setBadges] = useState<BadgeWithProgress[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && user) {
      fetchBadges()
    }
  }, [authLoading, user])

  const fetchBadges = async () => {
    try {
      const [allBadgesRes, userBadgesRes, booksRes] = await Promise.all([
        fetch("/api/badges/all"),
        fetch("/api/badges"),
        fetch("/api/books"),
      ])

      if (!allBadgesRes.ok || !userBadgesRes.ok || !booksRes.ok) {
        throw new Error("Failed to fetch data")
      }

      const allBadges: BadgeType[] = await allBadgesRes.json()
      const userBadges: UserBadge[] = await userBadgesRes.json()
      const books: Book[] = await booksRes.json()

      const earnedBadgeIds = new Set(userBadges.map((ub) => ub.badge_id))
      const earnedBadgesMap = new Map(userBadges.map((ub) => [ub.badge_id, ub.earned_at]))

      const bookCount = books.length
      const styles = new Set(books.map((b) => b.style))

      const badgesWithProgress: BadgeWithProgress[] = allBadges.map((badge) => {
        const earned = earnedBadgeIds.has(badge.id)
        let progress = 0
        let total = 1
        let description_progress = ""

        switch (badge.code) {
          case "first_book":
            progress = Math.min(bookCount, 1)
            total = 1
            description_progress = `${progress}/${total} livro criado`
            break
          case "five_books":
            progress = Math.min(bookCount, 5)
            total = 5
            description_progress = `${progress}/${total} livros criados`
            break
          case "ten_books":
            progress = Math.min(bookCount, 10)
            total = 10
            description_progress = `${progress}/${total} livros criados`
            break
          case "cartoon_style":
            progress = styles.has("cartoon") ? 1 : 0
            total = 1
            description_progress = progress ? "Estilo Cartoon usado" : "Use o estilo Cartoon"
            break
          case "manga_style":
            progress = styles.has("manga") ? 1 : 0
            total = 1
            description_progress = progress ? "Estilo Mangá usado" : "Use o estilo Mangá"
            break
          case "realistic_style":
            progress = styles.has("realistic") ? 1 : 0
            total = 1
            description_progress = progress ? "Estilo Realista usado" : "Use o estilo Realista"
            break
          case "classic_style":
            progress = styles.has("classic") ? 1 : 0
            total = 1
            description_progress = progress ? "Estilo Clássico usado" : "Use o estilo Clássico"
            break
          case "explorer":
            progress = styles.size
            total = 4
            description_progress = `${progress}/${total} estilos explorados`
            break
        }

        return {
          ...badge,
          earned,
          earnedAt: earnedBadgesMap.get(badge.id),
          progress,
          total,
          description_progress,
        }
      })

      // Sort: earned first, then by progress
      badgesWithProgress.sort((a, b) => {
        if (a.earned && !b.earned) return -1
        if (!a.earned && b.earned) return 1
        if (!a.earned && !b.earned) return b.progress / b.total - a.progress / a.total
        return 0
      })

      setBadges(badgesWithProgress)
    } catch (error) {
      console.error("Error fetching badges:", error)
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

  const earnedCount = badges.filter((b) => b.earned).length
  const totalCount = badges.length

  const categoryLabels = {
    creation: "Criação",
    milestone: "Marcos",
    style: "Estilos",
    special: "Especiais",
  }

  const categoryColors = {
    creation: "text-blue-500",
    milestone: "text-yellow-500",
    style: "text-purple-500",
    special: "text-pink-500",
  }

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

        <div className="mx-auto max-w-5xl">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="mb-4 flex justify-center">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent">
                <Trophy className="h-10 w-10 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold">Conquistas</h1>
            <p className="mt-2 text-muted-foreground">
              Você desbloqueou {earnedCount} de {totalCount} conquistas
            </p>
            <div className="mx-auto mt-4 max-w-md">
              <Progress value={(earnedCount / totalCount) * 100} className="h-2" />
            </div>
          </div>

          {/* Badges Grid */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {badges.map((badge) => (
              <Card
                key={badge.id}
                className={`relative overflow-hidden transition-all ${
                  badge.earned ? "border-primary/50 bg-primary/5" : "opacity-75"
                }`}
              >
                {badge.earned && (
                  <div className="absolute right-2 top-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                  </div>
                )}

                <CardHeader>
                  <div className="mb-3 flex items-center justify-center">
                    <div
                      className={`flex h-16 w-16 items-center justify-center rounded-full ${
                        badge.earned ? "bg-primary/20" : "bg-muted"
                      }`}
                    >
                      {badge.earned ? (
                        <Trophy className="h-8 w-8 text-primary" />
                      ) : (
                        <Lock className="h-8 w-8 text-muted-foreground" />
                      )}
                    </div>
                  </div>

                  <CardTitle className="text-center text-lg">{badge.name}</CardTitle>
                  <CardDescription className="text-center">{badge.description}</CardDescription>
                </CardHeader>

                <CardContent>
                  <div className="space-y-2">
                    <Badge variant="outline" className={`w-full justify-center ${categoryColors[badge.category]}`}>
                      {categoryLabels[badge.category]}
                    </Badge>

                    {!badge.earned && (
                      <>
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>{badge.description_progress}</span>
                          <span>{Math.round((badge.progress / badge.total) * 100)}%</span>
                        </div>
                        <Progress value={(badge.progress / badge.total) * 100} className="h-1" />
                      </>
                    )}

                    {badge.earned && badge.earnedAt && (
                      <p className="text-center text-xs text-muted-foreground">
                        Conquistado em {new Date(badge.earnedAt).toLocaleDateString("pt-BR")}
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Call to Action */}
          {earnedCount < totalCount && (
            <Card className="mt-8 border-dashed">
              <CardContent className="py-8 text-center">
                <Trophy className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
                <h3 className="mb-2 text-xl font-semibold">Continue criando para desbloquear mais conquistas!</h3>
                <p className="mb-4 text-muted-foreground">
                  Você ainda tem {totalCount - earnedCount} conquistas para desbloquear
                </p>
                <Link href="/app/create">
                  <Button className="gap-2">
                    <Sparkles className="h-4 w-4" />
                    Criar Novo Livro
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}
