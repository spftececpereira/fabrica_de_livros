import { NextResponse } from "next/server"
import { getSupabaseServerClient } from "@/lib/supabase/server"

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get("code")
  const origin = requestUrl.origin

  console.log("Auth callback received")
  console.log("Code present:", !!code)

  if (code) {
    const supabase = await getSupabaseServerClient()
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)

    if (!error && data.user) {
      console.log("Session exchange successful")

      const { error: userError } = await supabase.from("users").upsert(
        {
          id: data.user.id,
          email: data.user.email!,
          name: data.user.user_metadata?.full_name || data.user.user_metadata?.name || data.user.email?.split("@")[0],
          avatar_url: data.user.user_metadata?.avatar_url,
          provider: data.user.app_metadata?.provider || "google",
          provider_id: data.user.user_metadata?.sub,
        },
        {
          onConflict: "id",
        },
      )

      if (userError) {
        console.error("Error creating/updating user:", userError)
      } else {
        console.log("User synced to public.users table")
      }

      console.log("Redirecting to /app")
      return NextResponse.redirect(`${origin}/app`)
    } else {
      console.error("Session exchange error:", error)
    }
  }

  // Redirect to login on error
  console.log("Redirecting to login due to error or missing code")
  return NextResponse.redirect(`${origin}/login`)
}
