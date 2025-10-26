import { NextResponse } from "next/server"
import { getSupabaseServerClient } from "@/lib/supabase/server"

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const supabase = await getSupabaseServerClient()

    // Check authentication
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Get book with pages
    const { data: book, error: bookError } = await supabase
      .from("books")
      .select("*")
      .eq("id", id)
      .eq("user_id", user.id)
      .single()

    if (bookError || !book) {
      return NextResponse.json({ error: "Book not found" }, { status: 404 })
    }

    // Get pages
    const { data: pages, error: pagesError } = await supabase
      .from("pages")
      .select("*")
      .eq("book_id", id)
      .order("page_number", { ascending: true })

    if (pagesError) {
      console.error("Error fetching pages:", pagesError)
      return NextResponse.json({ error: "Failed to fetch pages" }, { status: 500 })
    }

    return NextResponse.json({ ...book, pages })
  } catch (error) {
    console.error("Error in GET /api/books/[id]:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params
    const supabase = await getSupabaseServerClient()

    // Check authentication
    const {
      data: { user },
    } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Delete book (cascade will delete pages)
    const { error } = await supabase.from("books").delete().eq("id", id).eq("user_id", user.id)

    if (error) {
      console.error("Error deleting book:", error)
      return NextResponse.json({ error: "Failed to delete book" }, { status: 500 })
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Error in DELETE /api/books/[id]:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
