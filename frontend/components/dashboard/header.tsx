'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Bell, Menu, Search, X } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { UserMenu } from './user-menu'
import { NotificationMenu } from './notification-menu'
import { ThemeToggle } from '@/components/theme-toggle'
import { WebSocketStatus } from '@/components/ui/websocket-status'

export function DashboardHeader() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Left side - Logo and Mobile Menu */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>

          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-sm font-bold">FL</span>
            </div>
            <span className="hidden sm:inline font-bold text-xl">
              Fábrica de Livros
            </span>
          </Link>
        </div>

        {/* Center - Search (hidden on mobile) */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Pesquisar livros..."
              className="pl-10 pr-4"
            />
          </div>
        </div>

        {/* Right side - Actions and User Menu */}
        <div className="flex items-center gap-2">
          {/* Search for mobile */}
          <Button variant="ghost" size="sm" className="md:hidden">
            <Search className="h-5 w-5" />
          </Button>

          {/* Notifications */}
          <NotificationMenu />

          {/* WebSocket Status */}
          <WebSocketStatus />

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* User Menu */}
          <UserMenu />
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="lg:hidden">
          <div className="fixed inset-0 z-40 bg-black/50" onClick={() => setIsMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 z-50 w-64 bg-background border-r">
            {/* Mobile sidebar content will go here */}
            <div className="p-4">
              <div className="mb-4">
                <Input placeholder="Pesquisar..." />
              </div>
              {/* Add mobile navigation items */}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}