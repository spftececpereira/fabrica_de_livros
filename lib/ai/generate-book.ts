import { getSupabaseServerClient } from "@/lib/supabase/server"
import type { CreateBookRequest } from "@/lib/types"
import { generateImage } from "./generate-image"
import { generateStory } from "./generate-story"
import { checkAndAwardBadges } from "@/lib/badges/check-badges"

export async function generateBook(bookId: string, request: CreateBookRequest) {
  const supabase = await getSupabaseServerClient()

  try {
    console.log("Starting book generation for book:", bookId)

    // Get book to verify it exists
    const { data: book, error: bookError } = await supabase.from("books").select("*").eq("id", bookId).single()

    if (bookError || !book) {
      console.error("Book not found:", bookError)
      throw new Error("Book not found")
    }

    // Generate story content if requested
    let storyContent = null
    if (request.has_story) {
      console.log("Generating story content...")
      storyContent = await generateStory(request.theme, request.pages_count)
      console.log("Story generated:", storyContent?.substring(0, 100))
    }

    // Update book with story content
    if (storyContent) {
      await supabase.from("books").update({ story_content: storyContent }).eq("id", bookId)
    }
    
    // Generate cover image - a colored cover representing the story
    let coverImageUrl = null;
    try {
      console.log("Generating cover image...")
      // Create a more descriptive prompt for the cover image that reflects the theme
      const coverPrompt = `A vibrant, colorful book cover illustration representing ${request.theme}. This should be a full-color artistic representation suitable as a book cover, with no text overlay. Style: ${request.style}. IMPORTANT: Do not add any text to the image. If there are thoughts of characters, represent them as thought bubbles with drawings only, no text. Avoid excessive shadows and fillings - characters should have clear outlines without filled areas. The main characters should never have filled areas, only clear outlines for coloring.`;
      
      // Use the OpenAI API to generate a colored cover image
      const { OpenAI } = await import("openai");
      const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
      
      const coverResponse = await openai.images.generate({
        model: "dall-e-3",
        prompt: coverPrompt,
        n: 1,
        size: "1024x1024",
        response_format: "b64_json",
      });
      
      if (coverResponse.data && coverResponse.data[0] && coverResponse.data[0].b64_json) {
        const coverBase64 = coverResponse.data[0].b64_json;
        const coverBuffer = Buffer.from(coverBase64, "base64");
        const coverImagePath = `cover-${bookId}-${Date.now()}.png`;
        
        const { error: coverUploadError } = await supabase.storage
          .from("books-images")
          .upload(coverImagePath, coverBuffer, {
            contentType: "image/png",
            upsert: true,
          });
          
        if (!coverUploadError) {
          const { data: coverSignedUrlData, error: coverSignedUrlError } = await supabase.storage
            .from("books-images")
            .createSignedUrl(coverImagePath, 3600); // URL expires in 1 hour
            
          if (!coverSignedUrlError) {
            coverImageUrl = coverSignedUrlData.signedUrl;
            // Update book record with cover image URL
            await supabase.from("books").update({ cover_image_url: coverImageUrl }).eq("id", bookId);
            console.log("Cover image generated and saved:", coverImageUrl);
          }
        }
      }
    } catch (coverError) {
      console.error("Error generating cover image:", coverError);
      // Continue without cover image if it fails
    }

    // Generate pages
    const pages = []
    for (let i = 1; i <= request.pages_count; i++) {
      try {
        console.log(`Generating page ${i}/${request.pages_count}`)

        const pageStory = storyContent ? storyContent.split(/\n\n+/).filter((p) => p.trim())[i - 1] || null : null

        // Generate image for this page
        const imageUrl = await generateImage(request.theme, request.style, i, request.pages_count, pageStory)

        console.log(`Image URL generated for page ${i}:`, imageUrl)

        // Save page to database
        const { data: page, error: pageError } = await supabase
          .from("pages")
          .insert({
            book_id: bookId,
            page_number: i,
            image_url: imageUrl,
            prompt: `${request.theme} - Página ${i}`,
            story_text: pageStory,
          })
          .select()
          .single()

        if (pageError) {
          console.error(`Error saving page ${i}:`, pageError)
          continue
        }

        console.log(`Page ${i} saved successfully`)
        pages.push(page)
      } catch (error) {
        console.error(`Error generating page ${i}:`, error)
        // Continue with next page even if one fails
      }
    }

    // Update book status
    const status = pages.length === request.pages_count ? "completed" : "failed"
    console.log(`Book generation ${status}. Pages generated: ${pages.length}/${request.pages_count}`)

    await supabase.from("books").update({ status }).eq("id", bookId)

    // Check and award badges
    if (status === "completed") {
      await checkAndAwardBadges(book.user_id, request.style)
    }

    return { bookId, status, pagesGenerated: pages.length }
  } catch (error) {
    console.error("Error generating book:", error)

    // Mark book as failed
    await supabase.from("books").update({ status: "failed" }).eq("id", bookId)

    throw error
  }
}
