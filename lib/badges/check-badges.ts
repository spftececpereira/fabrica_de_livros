import { getSupabaseServerClient } from "@/lib/supabase/server"
import type { ArtStyle } from "@/lib/types"

export async function checkAndAwardBadges(userId: string, style: ArtStyle) {
  const supabase = await getSupabaseServerClient()

  try {
    // Get user's book count
    const { data: books, error: booksError } = await supabase
      .from("books")
      .select("id, style, pages_count, has_story")
      .eq("user_id", userId)
      .eq("status", "completed")

    if (booksError || !books) {
      console.error("Error fetching books:", booksError)
      return []
    }

    const bookCount = books.length
    const styles = new Set(books.map((b) => b.style))
    const hasMaxPages = books.some((b) => b.pages_count === 20)
    const hasStory = books.some((b) => b.has_story)

    // Get all badges
    const { data: allBadges, error: badgesError } = await supabase.from("badges").select("*")

    if (badgesError || !allBadges) {
      console.error("Error fetching badges:", badgesError)
      return []
    }

    // Get user's current badges
    const { data: userBadges, error: userBadgesError } = await supabase
      .from("user_badges")
      .select("badge_id")
      .eq("user_id", userId)

    if (userBadgesError) {
      console.error("Error fetching user badges:", userBadgesError)
      return []
    }

    const earnedBadgeIds = new Set(userBadges?.map((ub) => ub.badge_id) || [])

    // Check which badges to award
    const badgesToAward = []
    const newBadges = []

    for (const badge of allBadges) {
      if (earnedBadgeIds.has(badge.id)) continue

      let shouldAward = false

      switch (badge.code) {
        case "first_book":
          shouldAward = bookCount >= 1
          break
        case "five_books":
          shouldAward = bookCount >= 5
          break
        case "ten_books":
          shouldAward = bookCount >= 10
          break
        case "cartoon_style":
          shouldAward = styles.has("cartoon")
          break
        case "manga_style":
          shouldAward = styles.has("manga")
          break
        case "realistic_style":
          shouldAward = styles.has("realistic")
          break
        case "classic_style":
          shouldAward = styles.has("classic")
          break
        case "explorer":
          shouldAward = styles.size >= 4
          break
        case "story_teller":
          shouldAward = hasStory
          break
        case "max_pages":
          shouldAward = hasMaxPages
          break
      }

      if (shouldAward) {
        badgesToAward.push(badge.id)
        newBadges.push(badge)
      }
    }

    // Award new badges
    if (badgesToAward.length > 0) {
      const { error: awardError } = await supabase
        .from("user_badges")
        .insert(badgesToAward.map((badgeId) => ({ user_id: userId, badge_id: badgeId })))

      if (awardError) {
        console.error("Error awarding badges:", awardError)
        return []
      }
    }

    return newBadges
  } catch (error) {
    console.error("Error checking badges:", error)
    return []
  }
}
