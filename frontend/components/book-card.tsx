import Link from "next/link"
import Image from "next/image" // Import next/image
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Clock, CheckCircle, AlertCircle, XCircle } from "lucide-react"
import { Book, bookHelpers } from "@/lib/types/book"

interface BookCardProps {
  book: Book
  onClick?: () => void
}

export function BookCard({ book, onClick }: BookCardProps) {
  const StatusIcon = {
    draft: AlertCircle,
    processing: Clock,
    completed: CheckCircle,
    failed: XCircle,
  }[book.status]

  return (
    <Link 
      href={`/dashboard/books/${book.id}`}
      onClick={(e) => {
        if (onClick) {
          e.preventDefault()
          onClick()
        }
      }}
    >
      <Card className="group h-full transition-all hover:shadow-lg hover:scale-105">
        <CardContent className="p-0">
          {/* Thumbnail */}
          <div className="aspect-[3/4] overflow-hidden rounded-t-lg bg-gradient-to-br from-primary/10 to-accent/10 relative">
            {book.cover_image ? (
              <Image 
                src={book.cover_image} 
                alt={book.title}
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                className="object-cover transition-transform group-hover:scale-110"
              />
            ) : (
              <div className="flex h-full items-center justify-center">
                <BookOpen className="h-16 w-16 text-primary/40 transition-transform group-hover:scale-110" />
              </div>
            )}
            
            {/* Status badge */}
            <div className="absolute top-2 right-2">
              <Badge className={`${bookHelpers.getStatusColor(book.status)} text-xs gap-1`}>
                <StatusIcon className="h-3 w-3" />
                {bookHelpers.getStatusLabel(book.status)}
              </Badge>
            </div>
          </div>

          {/* Book Info */}
          <div className="p-4 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold leading-tight line-clamp-2">{book.title}</h3>
            </div>

            {book.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">{book.description}</p>
            )}

            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{bookHelpers.getStyleLabel(book.style)}</span>
              <span>{book.pages_count} páginas</span>
            </div>

            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Criado em {new Date(book.created_at).toLocaleDateString('pt-BR')}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
