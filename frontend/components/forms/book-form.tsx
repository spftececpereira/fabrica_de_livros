'use client'

import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2, Palette, FileText } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
// Slider component removed during cleanup
import { Alert, AlertDescription } from '@/components/ui/alert'

import { BookStyle, BOOK_CONSTRAINTS, bookHelpers } from '@/lib/types/book'
import { bookCreateSchema, BookCreateFormData } from '@/lib/validation/schemas'
import { useCreateBook } from '@/lib/queries/book-queries'
import { usePermissions } from '@/lib/auth/use-auth'

interface BookFormProps {
  onSuccess?: (book: any) => void
  onCancel?: () => void
}

export function BookForm({ onSuccess, onCancel }: BookFormProps) {
  const createMutation = useCreateBook()
  const permissions = usePermissions()
  
  const form = useForm<BookCreateFormData>({
    resolver: zodResolver(bookCreateSchema),
    defaultValues: {
      title: '',
      description: '',
      pages_count: 8,
      style: BookStyle.CARTOON,
    },
  })

  const watchedPagesCount = form.watch('pages_count')

  const onSubmit = async (data: BookCreateFormData) => {
    if (!permissions.canCreateBooks) {
      return
    }

    try {
      const book = await createMutation.mutateAsync(data)
      form.reset()
      onSuccess?.(book)
    } catch (error) {
      // Error is handled by the mutation's onError
    }
  }

  if (permissions.hasReachedBookLimit) {
    return (
      <Card>
        <CardContent className="pt-6">
          <Alert>
            <AlertDescription>
              Você atingiu o limite de livros para sua conta. 
              {!permissions.canAccessPremium && (
                <span className="block mt-2">
                  <Button variant="outline" size="sm">
                    Fazer upgrade para Premium
                  </Button>
                </span>
              )}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Criar Novo Livro
        </CardTitle>
        <CardDescription>
          Defina os detalhes do seu livro de colorir personalizado
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {createMutation.error && (
            <Alert variant="destructive">
              <AlertDescription>
                {createMutation.error.message || 'Erro ao criar livro. Tente novamente.'}
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="title">Título do Livro</Label>
            <Input
              id="title"
              placeholder="Ex: Aventuras na Floresta Mágica"
              {...form.register('title')}
              error={form.formState.errors.title?.message}
              disabled={createMutation.isPending}
            />
            <p className="text-xs text-muted-foreground">
              {BOOK_CONSTRAINTS.MIN_TITLE_LENGTH}-{BOOK_CONSTRAINTS.MAX_TITLE_LENGTH} caracteres
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descrição (Opcional)</Label>
            <Textarea
              id="description"
              placeholder="Descreva o tema e estilo da sua história..."
              rows={3}
              {...form.register('description')}
              error={form.formState.errors.description?.message}
              disabled={createMutation.isPending}
            />
            <p className="text-xs text-muted-foreground">
              Máximo {BOOK_CONSTRAINTS.MAX_DESCRIPTION_LENGTH} caracteres
            </p>
          </div>

          <div className="space-y-4">
            <Label>Número de Páginas: {watchedPagesCount}</Label>
            <Controller
              control={form.control}
              name="pages_count"
              render={({ field }) => (
                <div className="space-y-3">
                  <Input
                    type="range"
                    min={BOOK_CONSTRAINTS.MIN_PAGES}
                    max={BOOK_CONSTRAINTS.MAX_PAGES}
                    step={1}
                    value={field.value}
                    onChange={(e) => field.onChange(Number(e.target.value))}
                    disabled={createMutation.isPending}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{BOOK_CONSTRAINTS.MIN_PAGES} páginas</span>
                    <span className="font-medium">{field.value} páginas</span>
                    <span>{BOOK_CONSTRAINTS.MAX_PAGES} páginas</span>
                  </div>
                </div>
              )}
            />
            {form.formState.errors.pages_count && (
              <p className="text-sm text-destructive">
                {form.formState.errors.pages_count.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="style">Estilo Artístico</Label>
            <Controller
              control={form.control}
              name="style"
              render={({ field }) => (
                <Select
                  value={field.value}
                  onValueChange={field.onChange}
                  disabled={createMutation.isPending}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Escolha um estilo" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.values(BookStyle).map((style) => (
                      <SelectItem key={style} value={style}>
                        <div className="flex items-center gap-2">
                          <Palette className="h-4 w-4" />
                          {bookHelpers.getStyleLabel(style)}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
            {form.formState.errors.style && (
              <p className="text-sm text-destructive">
                {form.formState.errors.style.message}
              </p>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <Button 
              type="submit" 
              disabled={createMutation.isPending || !permissions.canCreateBooks}
              className="flex-1"
            >
              {createMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Criando...
                </>
              ) : (
                'Criar Livro'
              )}
            </Button>
            
            {onCancel && (
              <Button 
                type="button" 
                variant="outline" 
                onClick={onCancel}
                disabled={createMutation.isPending}
              >
                Cancelar
              </Button>
            )}
          </div>

          <div className="text-xs text-muted-foreground bg-muted/50 p-3 rounded-md">
            <p className="font-medium mb-1">💡 Dica:</p>
            <p>
              Após criar o livro, você poderá iniciar a geração automática das páginas 
              e imagens usando nossa IA. O processo leva alguns minutos dependendo do 
              número de páginas.
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}