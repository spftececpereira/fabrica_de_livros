'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { fetchAPI } from '@/lib/api';
import { Download, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface Page {
    id: number;
    page_number: number;
    text_content: string;
    image_prompt: string;
    image_url?: string;
}

interface Book {
    id: number;
    title: string;
    theme: string;
    style: string;
    status: string;
    pages: Page[];
}

export default function BookReaderPage() {
    const params = useParams();
    const [book, setBook] = useState<Book | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadBook = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) throw new Error("Not authenticated");

                const data = await fetchAPI(`/api/v1/books/${params.id}`, { token });
                setBook(data);
            } catch (err: any) {
                setError(err.message || 'Failed to load book');
            } finally {
                setLoading(false);
            }
        };

        if (params.id) {
            loadBook();
        }
    }, [params.id]);

    const handleDownloadPDF = async () => {
        if (!book) return;
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/books/${book.id}/pdf`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!res.ok) throw new Error('Download failed');

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `book_${book.id}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error(err);
            alert('Failed to download PDF');
        }
    };

    if (loading) return <div className="flex justify-center p-12">Loading book...</div>;
    if (error) return <div className="p-12 text-destructive">Error: {error}</div>;
    if (!book) return <div className="p-12">Book not found</div>;

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <Link
                    href="/dashboard"
                    className="flex items-center text-muted-foreground hover:text-foreground transition-colors"
                >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Library
                </Link>

                <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${book.status === 'completed' ? 'bg-green-100 text-green-700' :
                            book.status === 'failed' ? 'bg-red-100 text-red-700' :
                                'bg-yellow-100 text-yellow-700'
                        }`}>
                        {book.status.toUpperCase()}
                    </span>
                    {(book.status === 'completed' || book.status === 'failed') && (
                        <button
                            onClick={handleDownloadPDF}
                            className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors"
                        >
                            <Download className="h-4 w-4" />
                            Download PDF
                        </button>
                    )}
                </div>
            </div>

            <div className="text-center space-y-2">
                <h1 className="text-4xl font-bold">{book.title}</h1>
                <p className="text-muted-foreground">
                    A {book.style} story about {book.theme}
                </p>
            </div>

            <div className="space-y-12">
                {book.pages.length === 0 ? (
                    <div className="text-center py-12 bg-card rounded-xl border border-border">
                        <p className="text-muted-foreground">
                            {book.status === 'generating'
                                ? 'Your story is being written by our magical elves...'
                                : 'No pages found. The generation might have failed.'}
                        </p>
                    </div>
                ) : (
                    book.pages.sort((a, b) => a.page_number - b.page_number).map((page) => (
                        <div key={page.id} className="bg-card rounded-xl shadow-sm border border-border overflow-hidden">
                            <div className="aspect-video bg-muted flex items-center justify-center relative">
                                {/* Placeholder for Image */}
                                <div className="text-center p-6">
                                    <p className="text-sm text-muted-foreground font-mono mb-2">Image Prompt:</p>
                                    <p className="text-sm italic opacity-70 max-w-lg">{page.image_prompt}</p>
                                </div>
                                <div className="absolute top-4 right-4 bg-background/80 backdrop-blur px-2 py-1 rounded text-xs font-mono">
                                    Page {page.page_number}
                                </div>
                            </div>
                            <div className="p-8 prose prose-lg dark:prose-invert max-w-none">
                                <p className="whitespace-pre-wrap leading-relaxed">{page.text_content}</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
