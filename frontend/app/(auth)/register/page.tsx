import type { Metadata } from "next"
import { RegisterForm } from "@/components/forms/register-form"

export const metadata: Metadata = {
  title: "Criar Conta - Fábrica de Livros",
  description: "Crie sua conta gratuita e comece a criar livros personalizados com IA",
}

export default function RegisterPage() {
  return <RegisterForm />
}