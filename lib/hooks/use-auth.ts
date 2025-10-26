"use client"

import { useEffect, useState } from "react"
import type { User } from "@supabase/supabase-js"
import { getSupabaseBrowserClient } from "@/lib/supabase/client"

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const supabase = getSupabaseBrowserClient()

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [supabase])

  const signInWithGoogle = async () => {
    console.log("Starting Google OAuth sign in...")

    const redirectUrl = process.env.NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL || `${window.location.origin}/auth/callback`
    console.log("Redirect URL:", redirectUrl)

    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: redirectUrl,
        queryParams: {
          access_type: "offline",
          prompt: "consent",
        },
      },
    })

    if (error) {
      console.error("OAuth error:", error)
      throw error
    }

    console.log("OAuth initiated successfully:", data)
    // Note: The browser will redirect to Google, so code after this may not execute
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  return {
    user,
    loading,
    signInWithGoogle,
    signOut,
  }
}
