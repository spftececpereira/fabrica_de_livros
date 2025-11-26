import { NextResponse } from "next/server"
import { getSupabaseServerClient } from "@/lib/supabase/server"
import { generateBook } from "@/lib/ai/generate-book"
import type { CreateBookRequest } from "@/lib/types"

export async function POST(request: Request) {
  try {
    const supabase = await getSupabaseServerClient()

    // Check authentication
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Parse and validate request
    const body = (await request.json()) as CreateBookRequest

    if (!body.title || body.title.length < 3 || body.title.length > 100) {
      return NextResponse.json({ error: "Invalid title" }, { status: 400 })
    }

    if (!body.theme || body.theme.length < 10 || body.theme.length > 500) {
      return NextResponse.json({ error: "Invalid theme" }, { status: 400 })
    }

    if (!["cartoon", "manga", "realistic", "classic"].includes(body.style)) {
      return NextResponse.json({ error: "Invalid style" }, { status: 400 })
    }

    if (body.pages_count < 1 || body.pages_count > 20) {
      return NextResponse.json({ error: "Invalid pages count" }, { status: 400 })
    }

    console.log("Creating book record with data:", {
      user_id: user.id,
      title: body.title,
      theme: body.theme,
      style: body.style,
      pages_count: body.pages_count,
      has_story: body.has_story,
      status: "generating",
    });
    
    // Create book record
    const { data: book, error: bookError } = await supabase
      .from("books")
      .insert({
        user_id: user.id,
        title: body.title,
        theme: body.theme,
        style: body.style,
        pages_count: body.pages_count,
        has_story: body.has_story,
        status: "generating",
      })
      .select()
      .single()
      
    console.log("Book creation result:", { book, bookError });

    if (bookError) {
      console.error("Error creating book:", bookError)
      return NextResponse.json({ error: "Failed to create book" }, { status: 500 })
    }

    // Start async generation (don't await)
    generateBook(book.id, body).catch((error) => {
      console.error("Error generating book:", error)
    })

    return NextResponse.json(book)
  } catch (error) {
    console.error("Error in POST /api/books:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

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

    // Get user's books
    const { data: books, error } = await supabase
      .from("books")
      .select("*")
      .eq("user_id", user.id)
      .order("created_at", { ascending: false })

    if (error) {
      console.error("Error fetching books:", error)
      return NextResponse.json({ error: "Failed to fetch books" }, { status: 500 })
    }

    return NextResponse.json(books)
  } catch (error) {
    console.error("Error in GET /api/books:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
