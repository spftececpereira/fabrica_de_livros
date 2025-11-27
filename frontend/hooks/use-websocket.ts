'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { useAuth } from '@/lib/auth/use-auth'
import { wsClient } from '@/lib/realtime/websocket-client'

interface UseWebSocketReturn {
  isConnected: boolean
  connectionState: string
  subscribe: (messageType: string, handler: (message: any) => void) => () => void
  subscribeToBookUpdates: (bookId: number) => void
}

export function useWebSocket(): UseWebSocketReturn {
  const { isAuthenticated, user } = useAuth()
  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState('disconnected')
  const connectionAttempted = useRef(false)

  // Update connection state
  useEffect(() => {
    const updateState = () => {
      setIsConnected(wsClient.isConnected)
      setConnectionState(wsClient.connectionState)
    }

    // Initial state
    updateState()

    // Poll for state changes
    const interval = setInterval(updateState, 1000)
    
    return () => clearInterval(interval)
  }, [])

  // Auto-connect when authenticated
  useEffect(() => {
    if (isAuthenticated && user && !connectionAttempted.current) {
      connectionAttempted.current = true
      
      wsClient.connect()
        .then(() => {
          console.log('WebSocket connected for user:', user.email)
        })
        .catch((error) => {
          console.error('Failed to connect WebSocket:', error)
          connectionAttempted.current = false // Allow retry
        })
    } else if (!isAuthenticated && wsClient.isConnected) {
      wsClient.disconnect()
      connectionAttempted.current = false
    }
  }, [isAuthenticated, user])

  // Disconnect on unmount
  useEffect(() => {
    return () => {
      if (wsClient.isConnected) {
        wsClient.disconnect()
      }
    }
  }, [])

  const subscribe = useCallback((messageType: string, handler: (message: any) => void) => {
    return wsClient.subscribe(messageType, handler)
  }, [])

  const subscribeToBookUpdates = useCallback((bookId: number) => {
    wsClient.subscribeToBookUpdates(bookId)
  }, [])

  return {
    isConnected,
    connectionState,
    subscribe,
    subscribeToBookUpdates,
  }
}

// Hook specifically for book generation updates
export function useBookGenerationUpdates(bookId?: number) {
  const { subscribe } = useWebSocket()
  const [generationStatus, setGenerationStatus] = useState<{
    taskId?: string
    status?: string
    progress?: number
    message?: string
    currentStep?: string
  }>({})

  useEffect(() => {
    if (!bookId) return

    const unsubscribe = subscribe('book_generation_update', (message) => {
      const { data } = message
      
      if (data.book_id === bookId) {
        setGenerationStatus({
          taskId: data.task_id,
          status: data.status,
          progress: data.progress,
          message: data.message,
          currentStep: data.current_step,
        })
      }
    })

    return unsubscribe
  }, [bookId, subscribe])

  return generationStatus
}

// Hook for general notifications
export function useNotifications() {
  const { subscribe } = useWebSocket()
  const [notifications, setNotifications] = useState<any[]>([])

  useEffect(() => {
    const unsubscribeNotifications = subscribe('notification', (message) => {
      setNotifications(prev => [message.data, ...prev.slice(0, 9)]) // Keep last 10
    })

    const unsubscribeSystem = subscribe('system_notification', (message) => {
      setNotifications(prev => [message.data, ...prev.slice(0, 9)])
    })

    return () => {
      unsubscribeNotifications()
      unsubscribeSystem()
    }
  }, [subscribe])

  const clearNotifications = useCallback(() => {
    setNotifications([])
  }, [])

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  return {
    notifications,
    clearNotifications,
    removeNotification,
  }
}