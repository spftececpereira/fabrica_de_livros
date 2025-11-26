"use client"

import { use, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { AppHeader } from "@/components/app-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, ArrowLeft, Download, Trash2, RefreshCw } from "lucide-react"
import Link from "next/link"
import type { Book, Page } from "@/lib/types"
import { generateBookPDF, downloadPDF } from "@/lib/pdf/generate-pdf"

export default function BookDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const [book, setBook] = useState<(Book & { pages?: Page[] }) | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    fetchBook()
    // Poll for updates if book is generating
    const interval = setInterval(() => {
      if (book?.status === "generating") {
        fetchBook()
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [id, book?.status])

  const fetchBook = async () => {
    try {
      const response = await fetch(`/api/books/${id}`)
      if (!response.ok) throw new Error("Failed to fetch book")
      const data = await response.json()
      setBook(data)
    } catch (error) {
      console.error("Error fetching book:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm("Tem certeza que deseja excluir este livro?")) return

    setDeleting(true)
    try {
      const response = await fetch(`/api/books/${id}`, { method: "DELETE" })
      if (!response.ok) throw new Error("Failed to delete book")
      router.push("/app")
    } catch (error) {
      console.error("Error deleting book:", error)
      setDeleting(false)
    }
  }

  const handleDownloadPDF = async () => {
    if (!book) return

    setGenerating(true)
    try {
      const pdf = await generateBookPDF(book)
      const filename = `${book.title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.pdf`
      downloadPDF(pdf, filename)
    } catch (error) {
      console.error("Error generating PDF:", error)
      alert("Erro ao gerar PDF. Tente novamente.")
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!book) {
    return (
      <div className="min-h-screen bg-background">
        <AppHeader />
        <main className="container mx-auto px-4 py-8">
          <p>Livro não encontrado</p>
        </main>
      </div>
    )
  }

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

        {/* Book Header */}
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-3">
              <h1 className="text-3xl font-bold">{book.title}</h1>
              <Badge className={statusColors[book.status]}>{statusLabels[book.status]}</Badge>
            </div>
            <p className="text-muted-foreground">{book.theme}</p>
            <div className="mt-2 flex gap-4 text-sm text-muted-foreground">
              <span>Estilo: {book.style}</span>
              <span>
                {book.pages?.length || 0}/{book.pages_count} páginas
              </span>
              {book.has_story && <span>Com história</span>}
            </div>
          </div>

          <div className="flex gap-2">
            {book.status === "completed" && (
              <Button onClick={handleDownloadPDF} disabled={generating} className="gap-2">
                {generating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Gerando PDF...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4" />
                    Baixar PDF
                  </>
                )}
              </Button>
            )}
            {book.status === "generating" && (
              <Button variant="outline" disabled className="gap-2 bg-transparent">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Gerando...
              </Button>
            )}
            <Button variant="destructive" onClick={handleDelete} disabled={deleting} className="gap-2">
              <Trash2 className="h-4 w-4" />
              Excluir
            </Button>
          </div>
        </div>

        {/* Pages Grid */}
        {book.status === "generating" && (
          <Card className="mb-8 border-yellow-500/50 bg-yellow-500/10">
            <CardContent className="flex items-center gap-3 py-4">
              <Loader2 className="h-5 w-5 animate-spin text-yellow-600" />
              <div>
                <p className="font-medium">Gerando seu livro...</p>
                <p className="text-sm text-muted-foreground">
                  Isso pode levar alguns minutos. Você pode sair desta página e voltar depois.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {book.pages?.map((page) => (
            <Card key={page.id}>
              <CardContent className="p-4">
                <div className="mb-3 aspect-[3/4] overflow-hidden rounded-lg bg-muted">
                  <img
                    src={page.image_url || "/placeholder.svg"}
                    alt={`Página ${page.page_number}`}
                    className="h-full w-full object-cover"
                  />
                </div>
                <div className="space-y-2">
                  <p className="font-medium">Página {page.page_number}</p>
                  {page.story_text && <p className="text-sm text-muted-foreground line-clamp-3">{page.story_text}</p>}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  )
}
