// Generic API Response Types
export interface APIResponse<T = unknown> {
  data?: T
  message?: string
  status: number
}

export interface APIError {
  detail: string
  field?: string
  error_code?: string
  details?: Record<string, unknown>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_previous: boolean
}

// Request/Response Types
export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: import('./user').User
}

export interface RefreshTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// Query Parameters
export interface BookFilters {
  status_filter?: string
  style_filter?: string
  search?: string
  skip?: number
  limit?: number
  sort_by?: 'created_at' | 'title' | 'updated_at'
  sort_order?: 'asc' | 'desc'
}

export interface UserFilters {
  role_filter?: string
  status_filter?: string
  search?: string
  skip?: number
  limit?: number
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string
  data: unknown
  timestamp: string
}

export interface BookGenerationMessage extends WebSocketMessage {
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

export interface NotificationMessage extends WebSocketMessage {
  type: 'notification'
  data: {
    id: string
    title: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    action_url?: string
  }
}

// File Upload Types
export interface FileUploadResponse {
  url: string
  filename: string
  size: number
  content_type: string
}

// Badge/Achievement Types
export interface Badge {
  id: number
  code: string
  name: string
  description: string | null
  icon: string | null
  category: BadgeCategory
  created_at: string
}

export interface UserBadge {
  id: number
  user_id: number
  badge_id: number
  earned_at: string
  badge: Badge
}

export enum BadgeCategory {
  CREATION = "creation",
  MILESTONE = "milestone", 
  STYLE = "style",
  SPECIAL = "special",
}

// Health Check Types
export interface HealthCheck {
  status: 'healthy' | 'unhealthy'
  version: string
  timestamp: string
  checks: {
    database: 'ok' | 'error'
    redis: 'ok' | 'error'
    ai_service: 'ok' | 'error'
  }
}

// Error Handling
export class APIErrorClass extends Error {
  public status: number
  public field?: string
  public error_code?: string
  public details?: Record<string, unknown>

  constructor(
    message: string,
    status: number = 500,
    field?: string,
    error_code?: string,
    details?: Record<string, unknown>
  ) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.field = field
    this.error_code = error_code
    this.details = details
  }
}

// Type Guards
export function isAPIError(error: unknown): error is APIError {
  return typeof error === 'object' && error !== null && 'detail' in error
}

export function isAuthResponse(data: unknown): data is AuthResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'access_token' in data &&
    'user' in data
  )
}