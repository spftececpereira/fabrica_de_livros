"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { BookOpen, LogOut, User, Library, Trophy } from "lucide-react"
import { useAuthContext } from "@/components/auth-provider"
import { useRouter } from "next/navigation"

export function AppHeader() {
  const { user, signOut } = useAuthContext()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
    router.push("/")
  }

  const getUserInitials = () => {
    if (!user?.user_metadata?.name) return "U"
    const names = user.user_metadata.name.split(" ")
    return names.length > 1 ? `${names[0][0]}${names[1][0]}` : names[0][0]
  }

  return (
    <header className="sticky top-0 z-50 border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="container mx-auto flex items-center justify-between px-4 py-3">
        <Link href="/app" className="flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-primary" />
          <span className="text-lg font-bold">Fábrica de Livros</span>
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/app">
            <Button variant="ghost" size="sm" className="gap-2">
              <Library className="h-4 w-4" />
              <span className="hidden sm:inline">Biblioteca</span>
            </Button>
          </Link>

          <Link href="/app/achievements">
            <Button variant="ghost" size="sm" className="gap-2">
              <Trophy className="h-4 w-4" />
              <span className="hidden sm:inline">Conquistas</span>
            </Button>
          </Link>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                <Avatar className="h-9 w-9">
                  <AvatarImage
                    src={user?.user_metadata?.avatar_url || "/placeholder.svg"}
                    alt={user?.user_metadata?.name || "User"}
                  />
                  <AvatarFallback className="bg-primary text-primary-foreground">{getUserInitials()}</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user?.user_metadata?.name || "Usuário"}</p>
                  <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/app/profile" className="flex cursor-pointer items-center">
                  <User className="mr-2 h-4 w-4" />
                  <span>Perfil</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleSignOut} className="cursor-pointer text-destructive">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Sair</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </nav>
      </div>
    </header>
  )
}
