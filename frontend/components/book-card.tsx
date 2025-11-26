import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen } from "lucide-react"
import type { Book } from "@/lib/types"

interface BookCardProps {
  book: Book
}

const statusColors = {
  generating: "bg-yellow-500",
  completed: "bg-green-500",
  failed: "bg-red-500",
}

const statusLabels = {
  generating: "Gerando",
  completed: "Concluído",
  failed: "Falhou",
}

const styleLabels = {
  cartoon: "Cartoon",
  manga: "Mangá",
  realistic: "Realista",
  classic: "Clássico",
}

export function BookCard({ book }: BookCardProps) {
  return (
    <Link href={`/app/books/${book.id}`}>
      <Card className="group h-full transition-all hover:shadow-lg">
        <CardContent className="p-4">
          {/* Thumbnail */}
          <div className="mb-3 aspect-[3/4] overflow-hidden rounded-lg bg-gradient-to-br from-primary/10 to-accent/10">
            <div className="flex h-full items-center justify-center">
              <BookOpen className="h-16 w-16 text-primary/40 transition-transform group-hover:scale-110" />
            </div>
          </div>

          {/* Book Info */}
          <div className="space-y-2">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold leading-tight line-clamp-2">{book.title}</h3>
              <Badge className={`${statusColors[book.status]} shrink-0 text-xs`}>{statusLabels[book.status]}</Badge>
            </div>

            <p className="text-sm text-muted-foreground line-clamp-2">{book.theme}</p>

            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{styleLabels[book.style]}</span>
              <span>{book.pages_count} páginas</span>
            </div>

            {book.has_story && (
              <Badge variant="outline" className="text-xs">
                Com história
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
