'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

interface Props {
  children?: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex items-center justify-center min-h-[400px] p-4">
          <Card className="w-full max-w-md border-destructive/50">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="p-3 rounded-full bg-destructive/10 text-destructive">
                  <AlertTriangle className="h-8 w-8" />
                </div>
              </div>
              <CardTitle className="text-xl text-destructive">Algo deu errado</CardTitle>
            </CardHeader>
            <CardContent className="text-center text-muted-foreground">
              <p>
                Ocorreu um erro inesperado ao carregar este componente.
                Nossa equipe técnica já foi notificada.
              </p>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <pre className="mt-4 p-2 bg-muted rounded text-xs text-left overflow-auto max-h-40">
                  {this.state.error.message}
                </pre>
              )}
            </CardContent>
            <CardFooter className="justify-center">
              <Button 
                variant="outline" 
                onClick={() => this.setState({ hasError: false })}
              >
                Tentar novamente
              </Button>
            </CardFooter>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
