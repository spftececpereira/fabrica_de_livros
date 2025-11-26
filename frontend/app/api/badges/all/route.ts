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

    // Get all badges
    const { data: badges, error } = await supabase.from("badges").select("*").order("category", { ascending: true })

    if (error) {
      console.error("Error fetching all badges:", error)
      return NextResponse.json({ error: "Failed to fetch badges" }, { status: 500 })
    }

    return NextResponse.json(badges)
  } catch (error) {
    console.error("Error in GET /api/badges/all:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
