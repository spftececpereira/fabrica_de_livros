import { getSupabaseServerClient } from "@/lib/supabase/server";
import type { ArtStyle } from "@/lib/types";
import { slugify } from "@/lib/utils";
import { Buffer } from "buffer";
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const STYLE_PROMPTS = {
  cartoon:
    "in a fun, colorful cartoon style with bold outlines, simple shapes, and playful characters. Lines should be thick and clearly defined for coloring. No text overlay, no filled areas, only clear black outlines ready for coloring.",
  manga:
    "in Japanese manga style with expressive lines, dynamic poses, and anime-inspired characters. Lines should be clearly defined for coloring. No text overlay, no filled areas, only clear black outlines ready for coloring.",
  realistic:
    "in a realistic style with natural proportions, simplified textures, and lifelike representation suitable for coloring. Lines should be clearly defined for coloring. No text overlay, no filled areas, only clear black outlines ready for coloring.",
  classic:
    "in a classic coloring book style with clean black outlines, simple details, and traditional composition. Lines should be thick and clearly defined for coloring. No text overlay, no filled areas, only clear black outlines ready for coloring.",
};

export async function generateImage(
  theme: string,
  style: ArtStyle,
  pageNumber: number,
  totalPages: number,
  storyText: string | null
): Promise<string> {
  const supabase = await getSupabaseServerClient();
  const stylePrompt = STYLE_PROMPTS[style];
  
  // Enhanced prompt with specific rules for coloring book images
  const prompt = `A black and white coloring book page ${stylePrompt}. Theme: ${theme}. Page ${pageNumber} of ${totalPages}. ${
    storyText ? `Scene: ${storyText}` : "The image should be kid-friendly, with thick and clear black outlines, high contrast, no filled areas, simple shapes, and ready for coloring. The image should have a clean background, well-separated elements that are easy to color individually, and no complex overlapping patterns. Lines should be bold and consistently thick throughout. IMPORTANT: Do not add any text to the image. If there are thoughts of characters, represent them as thought bubbles with drawings only, no text. Avoid excessive shadows and fillings - characters should have clear outlines without filled areas. The main characters should never have filled areas, only clear outlines for coloring."
  } `;

  try {
    console.log(
      "Generating image for page",
      pageNumber,
      "with theme:",
      theme
    );

    const imageResponse = await openai.images.generate({
      model: "dall-e-3", 
      prompt: prompt,
      n: 1,
      size: "1024x1024",
      response_format: "b64_json",
    });

    // Check if imageResponse.data exists and has content
    if (!imageResponse || !imageResponse.data || !imageResponse.data[0] || !imageResponse.data[0].b64_json) {
      throw new Error("No image data found in response");
    }

    const imageBase64 = imageResponse.data[0].b64_json;

    const imageBuffer = Buffer.from(imageBase64, "base64");
    const imagePath = `${slugify(theme)}-${Date.now()}.png`;

    const { error: uploadError } = await supabase.storage
      .from("books-images")
      .upload(imagePath, imageBuffer, {
        contentType: "image/png",
        upsert: true,
      });

    if (uploadError) {
      console.error("Error uploading image to Supabase:", uploadError);
      throw new Error("Failed to upload image");
    }

    const { data: signedUrlData, error: signedUrlError } = await supabase.storage
      .from("books-images")
      .createSignedUrl(imagePath, 3600); // URL expires in 1 hour

    if (signedUrlError) {
      throw new Error("Failed to create signed URL for image");
    }

    console.log(
      "Image generated and uploaded for page",
      pageNumber,
      "at",
      signedUrlData.signedUrl
    );
    return signedUrlData.signedUrl;
  } catch (error) {
    console.error("Error generating image:", error);
    throw error;
  }
}

