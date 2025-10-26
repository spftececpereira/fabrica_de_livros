"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BookOpen, Loader2 } from "lucide-react"
import { useAuth } from "@/lib/hooks/use-auth"
import { useState } from "react"
import { useToast } from "@/hooks/use-toast"

export default function LoginPage() {
  const router = useRouter()
  const { user, loading, signInWithGoogle } = useAuth()
  const [isSigningIn, setIsSigningIn] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    if (user && !loading) {
      router.push("/app")
    }
  }, [user, loading, router])

  const handleGoogleSignIn = async () => {
    try {
      console.log("User clicked Google sign in button")
      setIsSigningIn(true)
      await signInWithGoogle()
      // If we reach here, the redirect didn't happen - show error
      console.log("OAuth redirect did not occur")
    } catch (error) {
      console.error("Error signing in:", error)
      setIsSigningIn(false)
      toast({
        title: "Erro ao fazer login",
        description:
          error instanceof Error ? error.message : "Não foi possível conectar com o Google. Tente novamente.",
        variant: "destructive",
      })
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-background to-secondary/20 px-4">
      <Link href="/" className="mb-8 flex items-center gap-2">
        <BookOpen className="h-8 w-8 text-primary" />
        <span className="text-2xl font-bold">Fábrica de Livros</span>
      </Link>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Bem-vindo de volta</CardTitle>
          <CardDescription>Entre para continuar criando seus livros de colorir</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={handleGoogleSignIn}
            disabled={isSigningIn}
            className="w-full gap-2 bg-transparent"
            size="lg"
            variant="outline"
          >
            {isSigningIn ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
            )}
            Continuar com Google
          </Button>

          <div className="text-center text-sm text-muted-foreground">
            Não tem uma conta?{" "}
            <Link href="/signup" className="font-medium text-primary hover:underline">
              Criar conta
            </Link>
          </div>
        </CardContent>
      </Card>

      <p className="mt-8 text-center text-sm text-muted-foreground">
        Ao continuar, você concorda com nossos{" "}
        <Link href="/terms" className="underline hover:text-foreground">
          Termos de Serviço
        </Link>{" "}
        e{" "}
        <Link href="/privacy" className="underline hover:text-foreground">
          Política de Privacidade
        </Link>
      </p>
    </div>
  )
}
