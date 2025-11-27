'use client'

import { getAuthToken } from '../api'
import { toast } from 'sonner'

type MessageHandler = (message: any) => void

interface WebSocketMessage {
  type: string
  timestamp: number
  data: any
}

interface BookGenerationMessage {
  type: 'book_generation_update'
  data: {
    book_id: number
    task_id: string
    status: string
    progress: number
    message: string
    current_step?: string
  }
}

interface NotificationMessage {
  type: 'notification'
  data: {
    id: string
    title: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    action_url?: string
  }
}

class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private pingInterval: NodeJS.Timeout | null = null
  private isConnecting = false
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map()
  private isAuthenticated = false

  constructor() {
    const wsProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') || 'localhost:8000'
    this.url = `${wsProtocol}//${host}/api/v1/websocket/ws`
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
        resolve()
        return
      }

      this.isConnecting = true
      const token = getAuthToken()
      
      if (!token) {
        this.isConnecting = false
        reject(new Error('No authentication token available'))
        return
      }

      try {
        const wsUrl = `${this.url}?token=${encodeURIComponent(token)}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.isConnecting = false
          this.isAuthenticated = true
          this.reconnectAttempts = 0
          this.startPingInterval()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason)
          this.isConnecting = false
          this.isAuthenticated = false
          this.stopPingInterval()
          
          // Don't auto-reconnect if closed due to auth failure
          if (event.code === 4001) {
            console.error('WebSocket authentication failed')
            reject(new Error('Authentication failed'))
            return
          }

          // Auto-reconnect for other reasons
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect()
          } else {
            reject(new Error('Max reconnection attempts reached'))
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          
          if (this.reconnectAttempts === 0) {
            reject(error)
          }
        }

      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  disconnect() {
    this.stopPingInterval()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isAuthenticated = false
    this.messageHandlers.clear()
  }

  private scheduleReconnect() {
    setTimeout(() => {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      this.connect().catch((error) => {
        console.error('Reconnection failed:', error)
      })
    }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts))
  }

  private startPingInterval() {
    this.stopPingInterval()
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' })
      }
    }, 30000) // Ping every 30 seconds
  }

  private stopPingInterval() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  private send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  private handleMessage(message: WebSocketMessage) {
    const { type } = message

    // Handle system messages
    switch (type) {
      case 'connection_established':
        console.log('WebSocket connection established:', message.data)
        break
      
      case 'pong':
        // Response to our ping - connection is alive
        break
      
      case 'ping':
        // Server ping - respond with pong
        this.send({ type: 'pong' })
        break
      
      case 'book_generation_update':
        this.handleBookGenerationUpdate(message as BookGenerationMessage)
        break
      
      case 'notification':
        this.handleNotification(message as NotificationMessage)
        break
      
      case 'system_notification':
        this.handleSystemNotification(message)
        break
    }

    // Notify registered handlers
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in message handler:', error)
        }
      })
    }

    // Notify wildcard handlers
    const wildcardHandlers = this.messageHandlers.get('*')
    if (wildcardHandlers) {
      wildcardHandlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in wildcard message handler:', error)
        }
      })
    }
  }

  private handleBookGenerationUpdate(message: BookGenerationMessage) {
    const { data } = message
    
    if (data.status === 'completed') {
      toast.success(`Livro gerado com sucesso! 🎉`, {
        description: data.message,
        action: {
          label: 'Ver livro',
          onClick: () => {
            if (typeof window !== 'undefined') {
              window.location.href = `/dashboard/books/${data.book_id}`
            }
          }
        }
      })
    } else if (data.status === 'failed') {
      toast.error('Erro na geração do livro', {
        description: data.message
      })
    }
  }

  private handleNotification(message: NotificationMessage) {
    const { data } = message
    
    const toastConfig: any = {
      description: data.message
    }

    if (data.action_url) {
      toastConfig.action = {
        label: 'Ver',
        onClick: () => {
          if (typeof window !== 'undefined' && data.action_url) {
            window.location.href = data.action_url
          }
        }
      }
    }

    switch (data.type) {
      case 'success':
        toast.success(data.title, toastConfig)
        break
      case 'warning':
        toast.warning(data.title, toastConfig)
        break
      case 'error':
        toast.error(data.title, toastConfig)
        break
      default:
        toast.info(data.title, toastConfig)
    }
  }

  private handleSystemNotification(message: any) {
    const { data } = message
    
    toast.warning(data.title, {
      description: data.message,
      duration: 10000 // Longer duration for system notifications
    })
  }

  // Public API for subscribing to messages
  subscribe(messageType: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, new Set())
    }
    
    this.messageHandlers.get(messageType)!.add(handler)
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(messageType)
      if (handlers) {
        handlers.delete(handler)
        if (handlers.size === 0) {
          this.messageHandlers.delete(messageType)
        }
      }
    }
  }

  subscribeToBookUpdates(bookId: number) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({
        type: 'subscribe_book_updates',
        book_id: bookId
      })
    }
  }

  // Getters
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN && this.isAuthenticated
  }

  get connectionState(): string {
    if (!this.ws) return 'disconnected'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return this.isAuthenticated ? 'connected' : 'authenticating'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'disconnected'
      default: return 'unknown'
    }
  }
}

// Global WebSocket instance
export const wsClient = new WebSocketClient()

// Auto-connect when token is available
if (typeof window !== 'undefined') {
  // Connect when the module loads if we have a token
  const token = getAuthToken()
  if (token) {
    wsClient.connect().catch(error => {
      console.log('Initial WebSocket connection failed:', error.message)
    })
  }
}

export default wsClient