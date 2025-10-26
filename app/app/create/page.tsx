"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { AppHeader } from "@/components/app-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Loader2, Sparkles, ArrowLeft } from "lucide-react"
import Link from "next/link"
import type { ArtStyle } from "@/lib/types"

const STYLE_OPTIONS = [
  {
    value: "cartoon" as ArtStyle,
    label: "Cartoon",
    description: "Estilo divertido e colorido, perfeito para crianças",
    image: "/cartoon-coloring-book-style.jpg",
  },
  {
    value: "manga" as ArtStyle,
    label: "Mangá",
    description: "Estilo japonês com traços expressivos",
    image: "/manga-coloring-book-style.jpg",
  },
  {
    value: "realistic" as ArtStyle,
    label: "Realista",
    description: "Detalhes realistas e proporções naturais",
    image: "/realistic-coloring-book-style.jpg",
  },
  {
    value: "classic" as ArtStyle,
    label: "Clássico",
    description: "Estilo tradicional de livros de colorir",
    image: "/classic-coloring-book-style.jpg",
  },
]

export default function CreateBookPage() {
  const router = useRouter()
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    theme: "",
    style: "cartoon" as ArtStyle,
    pagesCount: 1,
    hasStory: false,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsCreating(true)

    try {
      const response = await fetch("/api/books", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: formData.title,
          theme: formData.theme,
          style: formData.style,
          pages_count: formData.pagesCount,
          has_story: formData.hasStory,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to create book")
      }

      const book = await response.json()
      router.push(`/app/books/${book.id}`)
    } catch (error) {
      console.error("Error creating book:", error)
      setIsCreating(false)
    }
  }

  const isFormValid = formData.title.length >= 3 && formData.theme.length >= 10

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

        <div className="mx-auto max-w-3xl">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-balance">Criar Novo Livro de Colorir</h1>
            <p className="mt-2 text-muted-foreground">Preencha os detalhes e deixe a IA criar algo incrível</p>
          </div>

          <form onSubmit={handleSubmit}>
            <Card>
              <CardHeader>
                <CardTitle>Detalhes do Livro</CardTitle>
                <CardDescription>Configure seu livro de colorir personalizado</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Title */}
                <div className="space-y-2">
                  <Label htmlFor="title">Título do Livro</Label>
                  <Input
                    id="title"
                    placeholder="Ex: Aventuras no Espaço"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    maxLength={100}
                    required
                  />
                  <p className="text-xs text-muted-foreground">{formData.title.length}/100 caracteres</p>
                </div>

                {/* Theme */}
                <div className="space-y-2">
                  <Label htmlFor="theme">Tema e Descrição</Label>
                  <Textarea
                    id="theme"
                    placeholder="Descreva o tema do seu livro. Ex: Astronautas explorando planetas coloridos, alienígenas amigáveis, foguetes e estrelas"
                    value={formData.theme}
                    onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
                    maxLength={500}
                    rows={4}
                    required
                  />
                  <p className="text-xs text-muted-foreground">{formData.theme.length}/500 caracteres (mínimo 10)</p>
                </div>

                {/* Style */}
                <div className="space-y-3">
                  <Label>Estilo Artístico</Label>
                  <RadioGroup
                    value={formData.style}
                    onValueChange={(value) => setFormData({ ...formData, style: value as ArtStyle })}
                    className="grid gap-4 sm:grid-cols-2"
                  >
                    {STYLE_OPTIONS.map((option) => (
                      <div key={option.value}>
                        <RadioGroupItem value={option.value} id={option.value} className="peer sr-only" />
                        <Label
                          htmlFor={option.value}
                          className="flex cursor-pointer flex-col items-center gap-3 rounded-lg border-2 border-muted bg-card p-4 hover:bg-accent peer-data-[state=checked]:border-primary"
                        >
                          <img
                            src={option.image || "/placeholder.svg"}
                            alt={option.label}
                            className="h-24 w-24 rounded-md object-cover"
                            loading="lazy"
                          />
                          <div className="text-center">
                            <div className="font-semibold">{option.label}</div>
                            <div className="text-xs text-muted-foreground">{option.description}</div>
                          </div>
                        </Label>
                      </div>
                    ))}
                  </RadioGroup>
                </div>

                {/* Pages Count */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label>Número de Páginas</Label>
                    <span className="text-sm font-medium">{formData.pagesCount} páginas</span>
                  </div>
                  <Slider
                    value={[formData.pagesCount]}
                    onValueChange={([value]) => setFormData({ ...formData, pagesCount: value })}
                    min={1}
                    max={20}
                    step={1}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground">Escolha entre 1 e 20 páginas</p>
                </div>

                {/* Story Option */}
                <div className="flex items-center justify-between rounded-lg border bg-muted/50 p-4">
                  <div className="space-y-0.5">
                    <Label htmlFor="hasStory" className="cursor-pointer">
                      Incluir História Educativa
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Adicione textos educativos em cada página para enriquecer a experiência
                    </p>
                  </div>
                  <Switch
                    id="hasStory"
                    checked={formData.hasStory}
                    onCheckedChange={(checked) => setFormData({ ...formData, hasStory: checked })}
                  />
                </div>

                {/* Submit Button */}
                <div className="flex gap-3 pt-4">
                  <Link href="/app" className="flex-1">
                    <Button type="button" variant="outline" className="w-full bg-transparent" disabled={isCreating}>
                      Cancelar
                    </Button>
                  </Link>
                  <Button type="submit" className="flex-1 gap-2" disabled={!isFormValid || isCreating}>
                    {isCreating ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Criando...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5" />
                        Criar Livro
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </form>
        </div>
      </main>
    </div>
  )
}
