'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  BookOpen, 
  Home, 
  Plus, 
  Settings, 
  User,
  BarChart3,
  Star,
  Crown
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth, usePermissions } from '@/lib/auth/use-auth'
import { UserRole } from '@/lib/types/user'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
  },
  {
    name: 'Meus Livros',
    href: '/dashboard/books',
    icon: BookOpen,
  },
  {
    name: 'Criar Livro',
    href: '/dashboard/books/create',
    icon: Plus,
  },
  {
    name: 'Estatísticas',
    href: '/dashboard/stats',
    icon: BarChart3,
    requiresPremium: true,
  },
  {
    name: 'Favoritos',
    href: '/dashboard/favorites',
    icon: Star,
    comingSoon: true,
  },
]

const settingsNavigation = [
  {
    name: 'Perfil',
    href: '/dashboard/profile',
    icon: User,
  },
  {
    name: 'Configurações',
    href: '/dashboard/settings',
    icon: Settings,
  },
]

export function DashboardSidebar() {
  const pathname = usePathname()
  const { user } = useAuth()
  const permissions = usePermissions()

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === href
    }
    return pathname.startsWith(href)
  }

  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
      <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-border bg-background px-6 pb-4 pt-20">
        {/* User Info */}
        {user && (
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
                {user.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.full_name}</p>
              <div className="flex items-center gap-2 mt-1">
                {user.role === UserRole.PREMIUM && (
                  <Badge variant="secondary" className="text-xs gap-1">
                    <Crown className="h-3 w-3" />
                    Premium
                  </Badge>
                )}
                {user.role === UserRole.ADMIN && (
                  <Badge variant="default" className="text-xs">
                    Admin
                  </Badge>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Main Navigation */}
        <nav className="flex flex-1 flex-col">
          <ul role="list" className="flex flex-1 flex-col gap-y-7">
            <li>
              <ul role="list" className="-mx-2 space-y-1">
                {navigation.map((item) => {
                  const isItemActive = isActive(item.href)
                  const isDisabled = (item.requiresPremium && !permissions.canAccessPremium) || item.comingSoon

                  return (
                    <li key={item.name}>
                      <Link
                        href={isDisabled ? '#' : item.href}
                        className={cn(
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors',
                          isItemActive
                            ? 'bg-primary text-primary-foreground'
                            : isDisabled
                            ? 'text-muted-foreground cursor-not-allowed'
                            : 'text-foreground hover:text-foreground hover:bg-muted'
                        )}
                        onClick={(e) => {
                          if (isDisabled) {
                            e.preventDefault()
                          }
                        }}
                      >
                        <item.icon
                          className={cn(
                            'h-6 w-6 shrink-0',
                            isItemActive ? 'text-primary-foreground' : 'text-muted-foreground group-hover:text-foreground'
                          )}
                        />
                        <span className="flex-1">{item.name}</span>
                        {item.requiresPremium && !permissions.canAccessPremium && (
                          <Crown className="h-4 w-4 text-yellow-500" />
                        )}
                        {item.comingSoon && (
                          <Badge variant="outline" className="text-xs">
                            Em breve
                          </Badge>
                        )}
                      </Link>
                    </li>
                  )
                })}
              </ul>
            </li>

            {/* Settings Section */}
            <li className="mt-auto">
              <div className="text-xs font-semibold leading-6 text-muted-foreground mb-2">
                Configurações
              </div>
              <ul role="list" className="-mx-2 space-y-1">
                {settingsNavigation.map((item) => {
                  const isItemActive = isActive(item.href)
                  
                  return (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={cn(
                          'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors',
                          isItemActive
                            ? 'bg-primary text-primary-foreground'
                            : 'text-foreground hover:text-foreground hover:bg-muted'
                        )}
                      >
                        <item.icon
                          className={cn(
                            'h-6 w-6 shrink-0',
                            isItemActive ? 'text-primary-foreground' : 'text-muted-foreground group-hover:text-foreground'
                          )}
                        />
                        {item.name}
                      </Link>
                    </li>
                  )
                })}
              </ul>

              {/* Upgrade CTA for free users */}
              {user?.role === UserRole.USER && (
                <div className="mt-4 p-3 rounded-lg bg-gradient-to-br from-purple-600/10 to-blue-600/10 border border-purple-200 dark:border-purple-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Crown className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm font-semibold">Premium</span>
                  </div>
                  <p className="text-xs text-muted-foreground mb-3">
                    Desbloqueie recursos avançados e crie livros ilimitados
                  </p>
                  <Button size="sm" className="w-full" asChild>
                    <Link href="/dashboard/upgrade">
                      Fazer Upgrade
                    </Link>
                  </Button>
                </div>
              )}
            </li>
          </ul>
        </nav>
      </div>
    </div>
  )
}