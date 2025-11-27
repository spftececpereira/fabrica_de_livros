import { z } from 'zod'
import { UserCreate } from './user' // Assuming UserCreate is already defined
import { BookStyle, BOOK_CONSTRAINTS } from '@/lib/types/book' // Import BookStyle and BOOK_CONSTRAINTS

// Existing schemas
export const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(1, 'Senha é obrigatória'),
})

export const registerSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'A senha deve ter pelo menos 8 caracteres'),
  full_name: z.string().min(2, 'O nome completo deve ter pelo menos 2 caracteres'),
})

// New schemas for password reset
export const forgotPasswordSchema = z.object({
  email: z.string().email('Email inválido'),
})

export const resetPasswordSchema = z.object({
  token: z.string().min(1, 'Token é obrigatório'),
  new_password: z.string().min(8, 'A nova senha deve ter pelo menos 8 caracteres'),
  confirm_password: z.string().min(8, 'Confirmação de senha é obrigatória'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'As senhas não coincidem',
  path: ['confirm_password'],
})

// Book schemas
export const bookCreateSchema = z.object({
  title: z.string()
    .min(BOOK_CONSTRAINTS.MIN_TITLE_LENGTH, `O título deve ter pelo menos ${BOOK_CONSTRAINTS.MIN_TITLE_LENGTH} caracteres`)
    .max(BOOK_CONSTRAINTS.MAX_TITLE_LENGTH, `O título deve ter no máximo ${BOOK_CONSTRAINTS.MAX_TITLE_LENGTH} caracteres`),
  description: z.string()
    .max(BOOK_CONSTRAINTS.MAX_DESCRIPTION_LENGTH, `A descrição deve ter no máximo ${BOOK_CONSTRAINTS.MAX_DESCRIPTION_LENGTH} caracteres`)
    .optional(),
  pages_count: z.number()
    .min(BOOK_CONSTRAINTS.MIN_PAGES, `O livro deve ter pelo menos ${BOOK_CONSTRAINTS.MIN_PAGES} páginas`)
    .max(BOOK_CONSTRAINTS.MAX_PAGES, `O livro deve ter no máximo ${BOOK_CONSTRAINTS.MAX_PAGES} páginas`),
  style: z.nativeEnum(BookStyle, {
    errorMap: () => ({ message: `O estilo deve ser um dos seguintes: ${BOOK_CONSTRAINTS.VALID_STYLES.join(', ')}` }),
  }),
})


// Infer types
export type LoginFormData = z.infer<typeof loginSchema>
export type RegisterFormData = z.infer<typeof registerSchema>
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>
export type BookCreateFormData = z.infer<typeof bookCreateSchema>