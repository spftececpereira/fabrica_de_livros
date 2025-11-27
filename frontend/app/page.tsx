'use client'

import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { BookOpen, Sparkles, Palette, Download, ArrowRight, Bot, Pencil, FileText } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"
import { AnimatedSection } from "@/components/animated-section"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold">Fábrica de Livros</span>
          </div>
          <nav className="flex items-center gap-4">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost">Entrar</Button>
            </Link>
            <Link href="/register">
              <Button>Começar Grátis</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-24 text-center">
        <div className="mx-auto max-w-4xl space-y-8">
          <h1 className="text-5xl font-extrabold tracking-tight lg:text-7xl">
            Crie livros de colorir únicos com <span className="bg-primary bg-clip-text text-transparent">inteligência artificial</span>
          </h1>
          <p className="text-xl text-muted-foreground">
            Transforme suas ideias em livros de colorir personalizados. Escolha o tema, o estilo artístico e deixe a IA
            criar páginas incríveis para você.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 pt-4 sm:flex-row">
            <Link href="/register">
              <Button size="lg" className="gap-2 btn-vibrant">
                <Sparkles className="h-5 w-5" />
                Criar Meu Primeiro Livro
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <Link href="#examples">
              <Button size="lg" variant="outline" className="btn-gradient">
                Ver Exemplos
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* How it works Section */}
      <AnimatedSection>
        <section className="py-20">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-4xl font-extrabold tracking-tight lg:text-5xl">Como funciona?</h2>
            <p className="mx-auto mt-6 max-w-2xl text-xl text-muted-foreground">É simples e rápido. Siga estes 3 passos:</p>
            <div className="mt-12 grid gap-12 md:grid-cols-3">
              <div className="card-wrapper">
                <div className="card-content flex flex-col items-center gap-4 p-6">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-2xl font-bold">1. Descreva sua ideia</h3>
                  <p className="text-muted-foreground">Diga à nossa IA qual o tema do livro e para qual idade ele se destina.</p>
                </div>
              </div>
              <div className="card-wrapper">
                <div className="card-content flex flex-col items-center gap-4 p-6">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-accent/10">
                    <Pencil className="h-8 w-8 text-accent" />
                  </div>
                  <h3 className="text-2xl font-bold">2. Escolha o estilo</h3>
                  <p className="text-muted-foreground">Selecione um dos 4 estilos artísticos: Cartoon, Mangá, Realista ou Clássico.</p>
                </div>
              </div>
              <div className="card-wrapper">
                <div className="card-content flex flex-col items-center gap-4 p-6">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-chart-2/10">
                    <FileText className="h-8 w-8 text-chart-2" />
                  </div>
                  <h3 className="text-2xl font-bold">3. Gere e baixe o PDF</h3>
                  <p className="text-muted-foreground">A IA cria o livro e você pode baixar o PDF em alta qualidade, pronto para imprimir.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </AnimatedSection>

      {/* Examples Section */}
      <AnimatedSection>
        <section id="examples" className="bg-secondary/50 py-20">
          <div className="container mx-auto px-4">
            <h2 className="text-center text-4xl font-extrabold tracking-tight lg:text-5xl">Exemplos de Livros</h2>
            <p className="mx-auto mt-6 max-w-2xl text-center text-xl text-muted-foreground">Veja alguns livros incríveis criados com a nossa plataforma.</p>
            <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
              <div className="card-wrapper">
                <div className="card-content p-4">
                  <Image src="/cartoon-coloring-book-style.jpg" alt="Cartoon style book" width={300} height={400} className="rounded-md" />
                  <h3 className="mt-4 text-lg font-bold">Estilo Cartoon</h3>
                </div>
              </div>
              <div className="card-wrapper">
                <div className="card-content p-4">
                  <Image src="/classic-coloring-book-style.jpg" alt="Classic style book" width={300} height={400} className="rounded-md" />
                  <h3 className="mt-4 text-lg font-bold">Estilo Clássico</h3>
                </div>
              </div>
              <div className="card-wrapper">
                <div className="card-content p-4">
                  <Image src="/manga-coloring-book-style.jpg" alt="Manga style book" width={300} height={400} className="rounded-md" />
                  <h3 className="mt-4 text-lg font-bold">Estilo Mangá</h3>
                </div>
              </div>
              <div className="card-wrapper">
                <div className="card-content p-4">
                  <Image src="/realistic-coloring-book-style.jpg" alt="Realistic style book" width={300} height={400} className="rounded-md" />
                  <h3 className="mt-4 text-lg font-bold">Estilo Realista</h3>
                </div>
              </div>
            </div>
          </div>
        </section>
      </AnimatedSection>

      {/* FAQ Section */}
      <AnimatedSection>
        <section className="py-20">
          <div className="container mx-auto max-w-3xl px-4">
            <h2 className="text-center text-4xl font-extrabold tracking-tight lg:text-5xl">Perguntas Frequentes</h2>
            <Accordion type="single" collapsible className="mt-12 w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Posso usar os livros para fins comerciais?</AccordionTrigger>
                <AccordionContent>
                  Sim, todos os livros criados na plataforma podem ser usados para fins comerciais. Você detém todos os direitos sobre as imagens geradas.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Quantos livros posso criar?</AccordionTrigger>
                <AccordionContent>
                  No plano gratuito, você pode criar até 3 livros. Em nossos planos pagos, você pode criar livros ilimitados.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Qual a resolução das imagens?</AccordionTrigger>
                <AccordionContent>
                  As imagens são geradas em alta resolução e o PDF final está no formato A4 com 300 DPI, ideal para impressão de alta qualidade.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-4">
                <AccordionTrigger>Posso personalizar o texto do livro?</AccordionTrigger>
                <AccordionContent>
                  Atualmente, a IA gera a história e as imagens. Estamos trabalhando em uma funcionalidade para permitir a edição do texto no futuro.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        </section>
      </AnimatedSection>

      {/* CTA Section */}
      <section className="py-24">
        <div className="container mx-auto max-w-3xl px-4 text-center">
          <h2 className="text-4xl font-extrabold tracking-tight lg:text-5xl">Pronto para criar seu primeiro livro?</h2>
          <p className="mx-auto mt-6 max-w-2xl text-xl text-muted-foreground">
            Junte-se a milhares de pais, professores e avós que já criaram livros incríveis.
          </p>
          <Link href="/register">
            <Button size="lg" className="mt-8 gap-2 btn-vibrant">
              <Sparkles className="h-5 w-5" />
              Começar Agora - É Grátis
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-secondary/50">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-muted-foreground">
          <p>© 2025 Fábrica de Livros. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  )
}
