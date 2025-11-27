export enum UserRole {
  USER = "user",
  PREMIUM = "premium",
  ADMIN = "admin",
}

export enum UserStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  PENDING = "pending",
}

export interface User {
  id: number
  email: string
  full_name: string
  role: UserRole
  status: UserStatus
  is_active: boolean
  is_verified: boolean
  last_login: string | null
  created_at: string
  updated_at: string | null
}

export interface UserCreate {
  email: string
  password: string
  full_name: string
}

export interface UserUpdate {
  email?: string
  full_name?: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface LoginRequest {
  username: string // email
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// Computed properties helpers
export const userHelpers = {
  isAdmin: (user: User): boolean => user.role === UserRole.ADMIN,
  isPremium: (user: User): boolean => [UserRole.PREMIUM, UserRole.ADMIN].includes(user.role),
  canCreateBooks: (user: User): boolean => user.is_active && user.status === UserStatus.ACTIVE,
  maxBooksAllowed: (user: User): number => {
    const limits = {
      [UserRole.USER]: 5,
      [UserRole.PREMIUM]: 50,
      [UserRole.ADMIN]: 999999
    }
    return limits[user.role] || 5
  }
}