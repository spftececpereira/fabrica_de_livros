import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function generateStory(theme: string, pagesCount: number): Promise<string> {
  const maxRetries = 5;
  for (let i = 0; i < maxRetries; i++) {
    try {
      const prompt = `Crie uma história educativa em PORTUGUÊS para um livro de colorir infantil com ${pagesCount} páginas. Tema: ${theme}. 

Escreva exatamente ${pagesCount} parágrafos curtos (um por página), cada um com 2-3 frases. Cada parágrafo deve:
- Ser educativo e apropriado para crianças de 4-8 anos
- Descrever uma cena que pode ser ilustrada
- Incluir fatos interessantes ou momentos de aprendizado
- Ser envolvente e divertido

IMPORTANTE: NÃO inclua numeração de páginas (como "Página 1:", "Page 1:", etc). Escreva apenas o texto da história.
Separe cada parágrafo com uma quebra de linha dupla.`

      const response = await openai.chat.completions.create({
        model: "gpt-4-turbo",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.8,
        max_tokens: 2048,
        top_p: 0.95,
      });

      let story = response.choices[0].message.content || ""

      // Remove common page number patterns
      story = story.replace(/Page \d+:\s*/gi, "")
      story = story.replace(/Página \d+:\s*/gi, "")
      story = story.replace(/^\d+\.\s*/gm, "")

      return story
    } catch (error) {
      if (i === maxRetries - 1) {
        console.error("Error generating story after multiple retries:", error)
        throw error
      }
      const delay = 2 ** i * 1000;
      console.log(`Error generating story. Retrying in ${delay / 1000}s... (Attempt ${i + 1}/${maxRetries})`);
      await new Promise(res => setTimeout(res, delay));
    }
  }
  throw new Error("Failed to generate story after multiple retries.");
}