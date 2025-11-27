'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { Eye, EyeOff, Loader2, Check, X } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'

import { useRegister } from '@/lib/queries/auth-queries'
import { registerSchema, RegisterFormData } from '@/lib/validation/schemas'

// Password strength checker
function getPasswordStrength(password: string): {
  score: number
  requirements: Array<{ text: string; met: boolean }>
} {
  const requirements = [
    { text: 'Pelo menos 8 caracteres', met: password.length >= 8 },
    { text: 'Uma letra maiúscula', met: /[A-Z]/.test(password) },
    { text: 'Uma letra minúscula', met: /[a-z]/.test(password) },
    { text: 'Um número', met: /[0-9]/.test(password) },
    { text: 'Um caractere especial', met: /[^A-Za-z0-9]/.test(password) },
  ]

  const metCount = requirements.filter(req => req.met).length
  const score = (metCount / requirements.length) * 100

  return { score, requirements }
}

export function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false)
  const router = useRouter()
  
  const registerMutation = useRegister()
  
  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      full_name: '',
    },
  })

  const watchedPassword = form.watch('password')
  const passwordStrength = getPasswordStrength(watchedPassword || '')

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await registerMutation.mutateAsync(data)
      router.push('/dashboard')
    } catch (error) {
      // Error is handled by the mutation's onError
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">
          Criar sua conta
        </CardTitle>
        <CardDescription className="text-center">
          Preencha os dados para começar a criar seus livros
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {registerMutation.error && (
            <Alert variant="destructive">
              <AlertDescription>
                {(registerMutation.error as any)?.response?.data?.detail || 
                 registerMutation.error.message || 
                 'Erro ao criar conta. Tente novamente.'}
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="full_name">Nome completo</Label>
            <Input
              id="full_name"
              type="text"
              placeholder="João Silva"
              {...form.register('full_name')}
              error={form.formState.errors.full_name?.message}
              disabled={registerMutation.isPending}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="seu@email.com"
              {...form.register('email')}
              error={form.formState.errors.email?.message}
              disabled={registerMutation.isPending}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Digite uma senha forte"
                {...form.register('password')}
                error={form.formState.errors.password?.message}
                disabled={registerMutation.isPending}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
                disabled={registerMutation.isPending}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
                <span className="sr-only">
                  {showPassword ? 'Hide password' : 'Show password'}
                </span>
              </Button>
            </div>

            {/* Password Strength Indicator */}
            {watchedPassword && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Força da senha:</span>
                  <span className={`font-medium ${
                    passwordStrength.score >= 80 ? 'text-green-600' :
                    passwordStrength.score >= 60 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {passwordStrength.score >= 80 ? 'Forte' :
                     passwordStrength.score >= 60 ? 'Média' :
                     'Fraca'}
                  </span>
                </div>
                <Progress 
                  value={passwordStrength.score} 
                  className="h-2"
                />
                <div className="space-y-1">
                  {passwordStrength.requirements.map((req, index) => (
                    <div key={index} className="flex items-center gap-2 text-xs">
                      {req.met ? (
                        <Check className="h-3 w-3 text-green-600" />
                      ) : (
                        <X className="h-3 w-3 text-red-600" />
                      )}
                      <span className={req.met ? 'text-green-600' : 'text-muted-foreground'}>
                        {req.text}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <Button 
            type="submit" 
            className="w-full"
            disabled={registerMutation.isPending || passwordStrength.score < 80}
          >
            {registerMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Criando conta...
              </>
            ) : (
              'Criar conta'
            )}
          </Button>

          <div className="text-center space-y-2">
            <div className="text-xs text-muted-foreground">
              Ao criar uma conta, você concorda com nossos{' '}
              <Link href="/terms" className="text-primary hover:underline">
                Termos de Uso
              </Link>{' '}
              e{' '}
              <Link href="/privacy" className="text-primary hover:underline">
                Política de Privacidade
              </Link>
            </div>
            
            <div className="text-sm text-muted-foreground">
              Já tem uma conta?{' '}
              <Link 
                href="/login" 
                className="text-primary hover:underline font-medium"
              >
                Fazer login
              </Link>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}