'use client'

import { Wifi, WifiOff, Loader2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { useWebSocket } from '@/hooks/use-websocket'

interface WebSocketStatusProps {
  showText?: boolean
  className?: string
}

export function WebSocketStatus({ showText = false, className = '' }: WebSocketStatusProps) {
  const { isConnected, connectionState } = useWebSocket()

  const getStatusInfo = () => {
    switch (connectionState) {
      case 'connected':
        return {
          icon: Wifi,
          color: 'bg-green-500',
          text: 'Conectado',
          description: 'Conectado ao servidor - notificações em tempo real ativas'
        }
      case 'connecting':
      case 'authenticating':
        return {
          icon: Loader2,
          color: 'bg-yellow-500',
          text: 'Conectando',
          description: 'Conectando ao servidor...'
        }
      case 'disconnected':
        return {
          icon: WifiOff,
          color: 'bg-red-500',
          text: 'Desconectado',
          description: 'Desconectado do servidor - notificações em tempo real indisponíveis'
        }
      case 'closing':
        return {
          icon: Loader2,
          color: 'bg-gray-500',
          text: 'Desconectando',
          description: 'Desconectando do servidor...'
        }
      default:
        return {
          icon: WifiOff,
          color: 'bg-gray-500',
          text: 'Desconhecido',
          description: 'Status da conexão desconhecido'
        }
    }
  }

  const statusInfo = getStatusInfo()
  const Icon = statusInfo.icon

  const StatusIndicator = () => (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="relative">
        <Icon 
          className={`h-4 w-4 ${
            connectionState === 'connecting' || connectionState === 'closing' 
              ? 'animate-spin' 
              : ''
          } ${isConnected ? 'text-green-600' : 'text-red-600'}`}
        />
        <div 
          className={`absolute -top-1 -right-1 h-2 w-2 rounded-full ${statusInfo.color}`} 
        />
      </div>
      {showText && (
        <span className="text-sm text-muted-foreground">
          {statusInfo.text}
        </span>
      )}
    </div>
  )

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="cursor-help">
            <StatusIndicator />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>{statusInfo.description}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

// Compact badge version
export function WebSocketStatusBadge() {
  const { isConnected, connectionState } = useWebSocket()

  const variant = isConnected ? 'default' : 'destructive'
  const text = isConnected ? 'Online' : 'Offline'

  return (
    <Badge variant={variant} className="text-xs">
      <div className={`w-2 h-2 rounded-full mr-1 ${
        isConnected ? 'bg-green-500' : 'bg-red-500'
      }`} />
      {text}
    </Badge>
  )
}