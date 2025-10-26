export type ArtStyle = "cartoon" | "manga" | "realistic" | "classic"

export type BookStatus = "generating" | "completed" | "failed"

export type BadgeCategory = "creation" | "milestone" | "style" | "special"

export interface User {
  id: string
  email: string
  name: string | null
  avatar_url: string | null
  provider: string
  provider_id: string | null
  created_at: string
  updated_at: string
}

export interface Book {
  id: string
  user_id: string
  title: string
  theme: string
  style: ArtStyle
  pages_count: number
  has_story: boolean
  story_content: string | null
  cover_image_url: string | null
  status: BookStatus
  created_at: string
  updated_at: string
}

export interface Page {
  id: string
  book_id: string
  page_number: number
  image_url: string
  prompt: string | null
  story_text: string | null
  created_at: string
}

export interface Badge {
  id: string
  code: string
  name: string
  description: string | null
  icon: string | null
  category: BadgeCategory
  created_at: string
}

export interface UserBadge {
  id: string
  user_id: string
  badge_id: string
  earned_at: string
  badge?: Badge
}

export interface CreateBookRequest {
  title: string
  theme: string
  style: ArtStyle
  pages_count: number
  has_story: boolean
}
