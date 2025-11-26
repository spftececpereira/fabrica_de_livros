import { NextResponse } from "next/server"
import { getSupabaseServerClient } from "@/lib/supabase/server"
import { jsPDF } from "jspdf"

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
      return NextResponse.json({ error: "Failed to fetch pages" }, { status: 500 })
    }

    // Generate PDF
    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4",
    })

    const pageWidth = 210
    const pageHeight = 297
    const margin = 15

    // Cover page with optional cover image
    if (book.cover_image_url) {
      // Add cover image if available
      try {
        const coverResponse = await fetch(book.cover_image_url);
        if (coverResponse.ok) {
          const coverBuffer = await coverResponse.arrayBuffer();
          const coverBase64 = Buffer.from(coverBuffer).toString('base64');
          
          // Determine image format from the original URL or response headers
          let format = 'JPEG';
          if (book.cover_image_url.includes('.png') || coverResponse.headers.get('content-type')?.includes('png')) {
            format = 'PNG';
          } else if (book.cover_image_url.includes('.jpg') || book.cover_image_url.includes('.jpeg') || coverResponse.headers.get('content-type')?.includes('jpeg')) {
            format = 'JPEG';
          }
          
          // Add image to cover - use most of the page but leave space for title
          const imgWidth = pageWidth - margin * 2;
          const imgHeight = 180; // Leave space at top and bottom for text
          const imgX = margin;
          const imgY = 40; // Leave space at top for title
          
          pdf.addImage(`data:image/${format.toLowerCase()};base64,${coverBase64}`, format, imgX, imgY, imgWidth, imgHeight);
          
          // Add title and other text over or around the image
          pdf.setFontSize(24)
          pdf.setFont("helvetica", "bold")
          pdf.setTextColor(0, 0, 0) // Black text
          const titleLines = pdf.splitTextToSize(book.title, pageWidth - margin * 2)
          let yPosition = 15 // Top position for title
          titleLines.forEach((line: string) => {
            pdf.text(line, pageWidth / 2, yPosition, { align: "center" })
            yPosition += 10
          })

          pdf.setFontSize(12)
          pdf.setFont("helvetica", "normal")
          yPosition += 10
          const themeLines = pdf.splitTextToSize(book.theme, pageWidth - margin * 4)
          themeLines.forEach((line: string) => {
            pdf.text(line, pageWidth / 2, yPosition, { align: "center" })
            yPosition += 7
          })

          pdf.setFontSize(10)
          pdf.setTextColor(128, 128, 128)
          pdf.text("Criado com Fábrica de Livros", pageWidth / 2, pageHeight - 20, { align: "center" })
          pdf.text(`${book.pages_count} páginas para colorir`, pageWidth / 2, pageHeight - 15, { align: "center" })
        } else {
          // Fallback to text-only cover if image fetch fails
          addTextOnlyCover();
        }
      } catch (coverError) {
        console.error("Error adding cover image to PDF:", coverError);
        // Fallback to text-only cover if there's an error
        addTextOnlyCover();
      }
    } else {
      // Fallback to text-only cover if no cover image URL
      addTextOnlyCover();
    }

    // Helper function for text-only cover
    function addTextOnlyCover() {
      pdf.setFontSize(24)
      pdf.setFont("helvetica", "bold")
      pdf.setTextColor(0, 0, 0)
      const titleLines = pdf.splitTextToSize(book.title, pageWidth - margin * 2)
      let yPosition = 60
      titleLines.forEach((line: string) => {
        pdf.text(line, pageWidth / 2, yPosition, { align: "center" })
        yPosition += 10
      })

      pdf.setFontSize(12)
      pdf.setFont("helvetica", "normal")
      yPosition += 10
      const themeLines = pdf.splitTextToSize(book.theme, pageWidth - margin * 4)
      themeLines.forEach((line: string) => {
        pdf.text(line, pageWidth / 2, yPosition, { align: "center" })
        yPosition += 7
      })

      pdf.setFontSize(10)
      pdf.setTextColor(128, 128, 128)
      pdf.text("Criado com Fábrica de Livros", pageWidth / 2, pageHeight - 20, { align: "center" })
      pdf.text(`${book.pages_count} páginas para colorir`, pageWidth / 2, pageHeight - 15, { align: "center" })
    }

    // Add content pages
    if (pages && pages.length > 0) {
      for (const page of pages) {
        pdf.addPage()

        pdf.setFontSize(10)
        pdf.setTextColor(128, 128, 128)
        pdf.text(`Página ${page.page_number}`, pageWidth / 2, margin, { align: "center" })

        if (page.story_text) {
          pdf.setFontSize(11)
          pdf.setTextColor(0, 0, 0)
          const storyLines = pdf.splitTextToSize(page.story_text, pageWidth - margin * 2)
          let storyY = margin + 10
          storyLines.forEach((line: string) => {
            pdf.text(line, margin, storyY)
            storyY += 6
          })
        }

        const imageY = page.story_text ? margin + 50 : margin + 20
        const availableHeight = pageHeight - imageY - margin - 10
        const availableWidth = pageWidth - margin * 2

        // Add image if available
        if (page.image_url) {
          try {
            // For server-side generation, we need to fetch the image data
            // We'll use fetch to get the image and convert it to a base64 string
            const imageResponse = await fetch(page.image_url);
            if (imageResponse.ok) {
              const imageBuffer = await imageResponse.arrayBuffer();
              const imageBase64 = Buffer.from(imageBuffer).toString('base64');
              
              // Determine image format from the original URL or response headers
              let format = 'JPEG';
              if (page.image_url.includes('.png') || imageResponse.headers.get('content-type')?.includes('png')) {
                format = 'PNG';
              } else if (page.image_url.includes('.jpg') || page.image_url.includes('.jpeg') || imageResponse.headers.get('content-type')?.includes('jpeg')) {
                format = 'JPEG';
              }
              
              // Calculate dimensions maintaining aspect ratio
              let imgWidth = availableWidth
              let imgHeight = availableHeight
              
              // Center the image horizontally
              const imgX = margin + (availableWidth - imgWidth) / 2
              
              // Add image to PDF using base64 data
              pdf.addImage(`data:image/${format.toLowerCase()};base64,${imageBase64}`, format, imgX, imageY, imgWidth, imgHeight)
            } else {
              // Fallback to placeholder if fetch fails
              pdf.setDrawColor(200, 200, 200)
              pdf.setLineWidth(0.5)
              pdf.rect(margin, imageY, availableWidth, availableHeight)

              pdf.setFontSize(10)
              pdf.setTextColor(150, 150, 150)
              pdf.text("Imagem para colorir", pageWidth / 2, imageY + availableHeight / 2, { align: "center" })
            }
          } catch (imageError) {
            console.error("Error adding image to PDF:", imageError)
            // Fallback to placeholder if there's an error
            pdf.setDrawColor(200, 200, 200)
            pdf.setLineWidth(0.5)
            pdf.rect(margin, imageY, availableWidth, availableHeight)

            pdf.setFontSize(10)
            pdf.setTextColor(150, 150, 150)
            pdf.text("Imagem para colorir", pageWidth / 2, imageY + availableHeight / 2, { align: "center" })
          }
        } else {
          // Fallback to placeholder if no image URL
          pdf.setDrawColor(200, 200, 200)
          pdf.setLineWidth(0.5)
          pdf.rect(margin, imageY, availableWidth, availableHeight)

          pdf.setFontSize(10)
          pdf.setTextColor(150, 150, 150)
          pdf.text("Imagem para colorir", pageWidth / 2, imageY + availableHeight / 2, { align: "center" })
        }
      }
    }

    // Return PDF as buffer
    const pdfBuffer = Buffer.from(pdf.output("arraybuffer"))

    return new NextResponse(pdfBuffer, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="${book.title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.pdf"`,
      },
    })
  } catch (error) {
    console.error("Error generating PDF:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
