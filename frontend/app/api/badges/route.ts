import { NextResponse } from "next/server"
import { getSupabaseServerClient } from "@/lib/supabase/server"

export async function GET(request: Request) {
  try {
    const supabase = await getSupabaseServerClient()

    // Check authentication
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get user's badges with badge details
    const { data: userBadges, error } = await supabase
      .from("user_badges")
      .select(`
        *,
        badge:badges(*)
      `)
      .eq("user_id", user.id)
      .order("earned_at", { ascending: false })

    if (error) {
      console.error("Error fetching badges:", error)
      return NextResponse.json({ error: "Failed to fetch badges" }, { status: 500 })
    }

    return NextResponse.json(userBadges)
  } catch (error) {
    console.error("Error in GET /api/badges:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
