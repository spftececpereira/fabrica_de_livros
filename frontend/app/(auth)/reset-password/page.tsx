'use client'

import { Suspense, useEffect, useState } from 'react' // Import Suspense
import { useRouter, useSearchParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'

import { resetPasswordSchema, ResetPasswordFormData } from '@/lib/validation/schemas'
import { api } from '@/lib/api'

// Client-only component to handle searchParams
function ResetPasswordContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [isError, setIsError] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const token = searchParams.get('token')

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      token: token || '',
      new_password: '',
      confirm_password: '',
    },
  })

  useEffect(() => {
    if (!token) {
      setIsError(true)
      setMessage('Token de redefinição de senha ausente.')
    }
    form.setValue('token', token || '') // Set token if present
  }, [token, form])

  const onSubmit = async (data: ResetPasswordFormData) => {
    setIsSubmitting(true)
    setMessage(null)
    setIsError(false)
    try {
      await api.post('/api/v1/auth/reset-password', {
        token: data.token,
        new_password: data.new_password,
      }, { skipErrorToast: true })
      setMessage('Sua senha foi redefinida com sucesso. Você pode fazer login agora.')
      toast.success('Senha redefinida com sucesso!')
      router.push('/login')
    } catch (error: any) {
      setIsError(true)
      setMessage(error.message || 'Erro ao redefinir senha. Verifique o token e tente novamente.')
      toast.error(error.message || 'Erro ao redefinir senha.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen py-12">
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Redefinir sua senha
          </CardTitle>
          <CardDescription className="text-center">
            Defina uma nova senha para sua conta.
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {message && (
              <Alert variant={isError ? "destructive" : "default"}>
                <AlertDescription>{message}</AlertDescription>
              </Alert>
            )}

            {isError && !token && (
                 <Alert variant="destructive">
                    <AlertDescription>
                        Token de redefinição de senha inválido ou ausente. Por favor, solicite um novo link.
                    </AlertDescription>
                 </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="new_password">Nova Senha</Label>
              <div className="relative">
                <Input
                  id="new_password"
                  type={showNewPassword ? 'text' : 'password'}
                  placeholder="Digite sua nova senha forte"
                  {...form.register('new_password')}
                  error={form.formState.errors.new_password?.message}
                  disabled={isSubmitting}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  disabled={isSubmitting}
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                  <span className="sr-only">
                    {showNewPassword ? 'Hide password' : 'Show password'}
                  </span>
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm_password">Confirmar Nova Senha</Label>
              <div className="relative">
                <Input
                  id="confirm_password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Confirme sua nova senha"
                  {...form.register('confirm_password')}
                  error={form.formState.errors.confirm_password?.message}
                  disabled={isSubmitting}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  disabled={isSubmitting}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                  <span className="sr-only">
                    {showConfirmPassword ? 'Hide password' : 'Show password'}
                  </span>
                </Button>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Redefinindo...
                </>
              ) : (
                'Redefinir Senha'
              )}
            </Button>

            <div className="text-center text-sm text-muted-foreground">
              <Link 
                href="/login" 
                className="text-primary hover:underline font-medium"
              >
                Voltar para o login
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div>Carregando redefinição de senha...</div>}>
      <ResetPasswordContent />
    </Suspense>
  )
}