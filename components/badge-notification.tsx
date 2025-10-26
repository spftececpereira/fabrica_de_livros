"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Trophy, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Badge } from "@/lib/types"

interface BadgeNotificationProps {
  badge: Badge
  onClose: () => void
}

export function BadgeNotification({ badge, onClose }: BadgeNotificationProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Animate in
    setTimeout(() => setIsVisible(true), 100)

    // Auto close after 5 seconds
    const timer = setTimeout(() => {
      handleClose()
    }, 5000)

    return () => clearTimeout(timer)
  }, [])

  const handleClose = () => {
    setIsVisible(false)
    setTimeout(onClose, 300)
  }

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 transition-all duration-300 ${
        isVisible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
      }`}
    >
      <Card className="w-80 border-primary/50 bg-gradient-to-br from-primary/10 to-accent/10 shadow-lg">
        <CardContent className="relative p-4">
          <Button variant="ghost" size="icon" className="absolute right-2 top-2 h-6 w-6" onClick={handleClose}>
            <X className="h-4 w-4" />
          </Button>

          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/20">
              <Trophy className="h-6 w-6 text-primary" />
            </div>

            <div className="flex-1">
              <p className="mb-1 text-sm font-medium text-primary">Nova Conquista Desbloqueada!</p>
              <h3 className="font-semibold">{badge.name}</h3>
              <p className="text-sm text-muted-foreground">{badge.description}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
