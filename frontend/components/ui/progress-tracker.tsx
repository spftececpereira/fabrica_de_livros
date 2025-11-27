'use client'

import { useEffect, useState } from 'react'
import { CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

interface ProgressStep {
  id: string
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  progress?: number
}

interface ProgressTrackerProps {
  steps: ProgressStep[]
  currentStep?: string
  overallProgress?: number
  className?: string
}

export function ProgressTracker({
  steps,
  currentStep,
  overallProgress = 0,
  className = ''
}: ProgressTrackerProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Overall Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium">Progresso Geral</span>
          <span className="text-muted-foreground">{Math.round(overallProgress)}%</span>
        </div>
        <Progress value={overallProgress} className="h-2" />
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => {
          const isActive = currentStep === step.id
          const isCompleted = step.status === 'completed'
          const isError = step.status === 'error'
          const isPending = step.status === 'pending'
          
          const StepIcon = () => {
            if (isCompleted) return <CheckCircle className="h-5 w-5 text-green-600" />
            if (isError) return <AlertCircle className="h-5 w-5 text-red-600" />
            if (isActive) return <Clock className="h-5 w-5 text-blue-600 animate-pulse" />
            return <div className="h-5 w-5 rounded-full border-2 border-muted-foreground" />
          }

          return (
            <div key={step.id} className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                <StepIcon />
              </div>
              
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className={`text-sm font-medium ${
                    isActive ? 'text-primary' : 
                    isCompleted ? 'text-green-700 dark:text-green-400' :
                    isError ? 'text-red-700 dark:text-red-400' :
                    'text-muted-foreground'
                  }`}>
                    {step.title}
                  </h4>
                  
                  <Badge variant={
                    isCompleted ? 'default' :
                    isError ? 'destructive' :
                    isActive ? 'secondary' :
                    'outline'
                  } className="text-xs">
                    {isCompleted ? 'Concluído' :
                     isError ? 'Erro' :
                     isActive ? 'Em progresso' :
                     'Pendente'}
                  </Badge>
                </div>
                
                {step.description && (
                  <p className="text-xs text-muted-foreground">
                    {step.description}
                  </p>
                )}
                
                {/* Individual step progress */}
                {isActive && typeof step.progress === 'number' && (
                  <div className="mt-2">
                    <Progress value={step.progress} className="h-1" />
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Hook for managing progress tracking
export function useProgressTracker(initialSteps: Omit<ProgressStep, 'status'>[]) {
  const [steps, setSteps] = useState<ProgressStep[]>(
    initialSteps.map(step => ({ ...step, status: 'pending' }))
  )
  const [currentStep, setCurrentStep] = useState<string | null>(null)
  const [overallProgress, setOverallProgress] = useState(0)

  const updateStep = (stepId: string, updates: Partial<ProgressStep>) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, ...updates } : step
    ))
  }

  const startStep = (stepId: string) => {
    setCurrentStep(stepId)
    updateStep(stepId, { status: 'in_progress' })
  }

  const completeStep = (stepId: string) => {
    updateStep(stepId, { status: 'completed', progress: 100 })
    
    // Find next pending step
    const currentIndex = steps.findIndex(s => s.id === stepId)
    const nextStep = steps[currentIndex + 1]
    
    if (nextStep && nextStep.status === 'pending') {
      setCurrentStep(nextStep.id)
    } else {
      setCurrentStep(null)
    }
  }

  const errorStep = (stepId: string, error?: string) => {
    updateStep(stepId, { 
      status: 'error', 
      description: error || 'Ocorreu um erro nesta etapa'
    })
    setCurrentStep(null)
  }

  const updateStepProgress = (stepId: string, progress: number) => {
    updateStep(stepId, { progress })
  }

  const reset = () => {
    setSteps(prev => prev.map(step => ({ ...step, status: 'pending', progress: 0 })))
    setCurrentStep(null)
    setOverallProgress(0)
  }

  // Calculate overall progress
  useEffect(() => {
    const completedSteps = steps.filter(s => s.status === 'completed').length
    const totalSteps = steps.length
    const currentStepProgress = currentStep ? 
      (steps.find(s => s.id === currentStep)?.progress || 0) : 0
    
    const progress = totalSteps > 0 ? 
      ((completedSteps / totalSteps) * 100) + 
      (currentStepProgress / totalSteps) : 0
    
    setOverallProgress(Math.min(progress, 100))
  }, [steps, currentStep])

  return {
    steps,
    currentStep,
    overallProgress,
    startStep,
    completeStep,
    errorStep,
    updateStep,
    updateStepProgress,
    reset
  }
}