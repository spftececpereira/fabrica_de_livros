import { jsPDF } from "jspdf"
import type { Book, Page } from "@/lib/types"

export async function generateBookPDF(book: Book & { pages?: Page[] }) {
  // Create PDF in A4 format (210mm x 297mm)
  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  })

  const pageWidth = 210
  const pageHeight = 297
  const margin = 15

  // Add cover page with optional cover image
  if (book.cover_image_url) {
    // Add cover image if available
    try {
      if (book.cover_image_url.startsWith('data:')) {
        // It's a data URL, we can use it directly
        let format = 'JPEG';
        if (book.cover_image_url.includes('image/png')) format = 'PNG';
        else if (book.cover_image_url.includes('image/jpeg')) format = 'JPEG';
        else if (book.cover_image_url.includes('image/jpg')) format = 'JPEG';
        
        // Add image to cover - use most of the page but leave space for title
        const imgWidth = pageWidth - margin * 2;
        const imgHeight = 180; // Leave space at top and bottom for text
        const imgX = margin;
        const imgY = 40; // Leave space at top for title
        
        pdf.addImage(book.cover_image_url, format, imgX, imgY, imgWidth, imgHeight);
        
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
      } else if (typeof window !== 'undefined') {
        // Browser environment - we need to fetch the image
        const coverResponse = await fetch(book.cover_image_url);
        if (coverResponse.ok) {
          const coverBlob = await coverResponse.blob();
          const coverBuffer = await coverBlob.arrayBuffer();
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
      } else {
        // Server environment - fallback to text-only cover
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

  // Add pages
  if (book.pages && book.pages.length > 0) {
    for (let i = 0; i < book.pages.length; i++) {
      const page = book.pages[i]

      pdf.addPage()

      // Page number
      pdf.setFontSize(10)
      pdf.setTextColor(128, 128, 128)
      pdf.text(`Página ${page.page_number}`, pageWidth / 2, margin, { align: "center" })

      // Story text if available
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

      // Add image
      try {
        // Calculate image dimensions to fit page while maintaining aspect ratio
        const imageY = page.story_text ? margin + 50 : margin + 20
        const availableHeight = pageHeight - imageY - margin - 10
        const availableWidth = pageWidth - margin * 2

        // Load and add the actual image
        if (page.image_url) {
          // Check if image_url is a data URL (base64 encoded image)
          if (page.image_url.startsWith('data:')) {
            // Calculate dimensions maintaining aspect ratio
            let imgWidth = availableWidth
            let imgHeight = availableHeight
            
            // Center the image horizontally
            const imgX = margin + (availableWidth - imgWidth) / 2
            
            // Determine image format from data URL
            let format = 'JPEG';
            if (page.image_url.includes('image/png')) format = 'PNG';
            else if (page.image_url.includes('image/jpeg')) format = 'JPEG';
            else if (page.image_url.includes('image/jpg')) format = 'JPEG';
            
            // Add image to PDF
            pdf.addImage(page.image_url, format, imgX, imageY, imgWidth, imgHeight)
          } else {
            // For regular URLs, we fetch the image data
            // This would work in a browser environment
            if (typeof window !== 'undefined') {
              // Browser environment - we need to fetch the image
              const imageResponse = await fetch(page.image_url);
              if (imageResponse.ok) {
                const imageBlob = await imageResponse.blob();
                const imageBuffer = await imageBlob.arrayBuffer();
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
                const imgWidth = availableWidth
                const imgHeight = availableHeight
                
                pdf.setDrawColor(200, 200, 200)
                pdf.setLineWidth(0.5)
                pdf.rect(margin, imageY, imgWidth, imgHeight)
                
                pdf.setFontSize(10)
                pdf.setTextColor(150, 150, 150)
                pdf.text("Imagem para colorir", pageWidth / 2, imageY + imgHeight / 2, { align: "center" })
              }
            } else {
              // Server environment - we still use a placeholder since we can't easily fetch images in this context
              // The main PDF generation happens in the API route, so this function is primarily for client-side usage
              const imgWidth = availableWidth
              const imgHeight = availableHeight
              
              pdf.setDrawColor(200, 200, 200)
              pdf.setLineWidth(0.5)
              pdf.rect(margin, imageY, imgWidth, imgHeight)
              
              pdf.setFontSize(10)
              pdf.setTextColor(150, 150, 150)
              pdf.text("Imagem para colorir", pageWidth / 2, imageY + imgHeight / 2, { align: "center" })
            }
          }
        } else {
          // Fallback to placeholder if no image URL
          const imgWidth = availableWidth
          const imgHeight = availableHeight
          
          pdf.setDrawColor(200, 200, 200)
          pdf.setLineWidth(0.5)
          pdf.rect(margin, imageY, imgWidth, imgHeight)
          
          pdf.setFontSize(10)
          pdf.setTextColor(150, 150, 150)
          pdf.text("Imagem para colorir", pageWidth / 2, imageY + imgHeight / 2, { align: "center" })
        }
      } catch (error) {
        console.error("Error adding image to PDF:", error)
        
        // Fallback to placeholder if there's an error
        const imageY = page.story_text ? margin + 50 : margin + 20
        const availableHeight = pageHeight - imageY - margin - 10
        const availableWidth = pageWidth - margin * 2
        const imgWidth = availableWidth
        const imgHeight = availableHeight
        
        pdf.setDrawColor(200, 200, 200)
        pdf.setLineWidth(0.5)
        pdf.rect(margin, imageY, imgWidth, imgHeight)
        
        pdf.setFontSize(10)
        pdf.setTextColor(150, 150, 150)
        pdf.text("Imagem para colorir", pageWidth / 2, imageY + imgHeight / 2, { align: "center" })
      }
    }
  }

  return pdf
}

export function downloadPDF(pdf: jsPDF, filename: string) {
  pdf.save(filename)
}
