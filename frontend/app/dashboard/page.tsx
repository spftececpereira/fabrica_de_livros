'use client';

import { useEffect, useState } from 'react';
import { fetchAPI } from '@/lib/api';
import Link from 'next/link';
import { Plus } from 'lucide-react';

interface Book {
    id: number;
    title: string;
    theme: string;
    status: string;
    created_at: string;
}

export default function DashboardPage() {
    const [books, setBooks] = useState<Book[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadBooks = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) return;

                const data = await fetchAPI('/api/v1/books/', { token });
                setBooks(data);
            } catch (error) {
                console.error('Failed to load books:', error);
            } finally {
                setLoading(false);
            }
        };

        loadBooks();
    }, []);

    if (loading) {
        return <div className="flex justify-center p-12">Loading books...</div>;
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">My Library</h2>
                <Link
                    href="/dashboard/create"
                    className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90 transition-colors gap-2"
                >
                    <Plus className="h-4 w-4" />
                    New Book
                </Link>
            </div>

            {books.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-border rounded-xl">
                    <h3 className="text-lg font-medium text-muted-foreground">No books yet</h3>
                    <p className="text-sm text-muted-foreground mt-1">Create your first magical story!</p>
                </div>
            ) : (
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    {books.map((book) => (
                        <div key={book.id} className="card-wrapper group">
                            <div className="card-content p-6 flex flex-col h-full">
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-4">
                                        <span className={`px-2 py-1 text-xs rounded-full ${book.status === 'completed' ? 'bg-green-100 text-green-700' :
                                                book.status === 'failed' ? 'bg-red-100 text-red-700' :
                                                    'bg-yellow-100 text-yellow-700'
                                            }`}>
                                            {book.status}
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                            {new Date(book.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">{book.title}</h3>
                                    <p className="text-sm text-muted-foreground">Theme: {book.theme}</p>
                                </div>

                                <div className="mt-6 pt-4 border-t border-border flex gap-2">
                                    <Link
                                        href={`/dashboard/books/${book.id}`}
                                        className="flex-1 text-center px-3 py-2 text-sm font-medium text-primary bg-primary/10 rounded-md hover:bg-primary/20 transition-colors"
                                    >
                                        Read
                                    </Link>
                                    {book.status === 'completed' || book.status === 'failed' ? ( // Allow download even if failed for testing
                                        <button
                                            onClick={async () => {
                                                const token = localStorage.getItem('token');
                                                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/books/${book.id}/pdf`, {
                                                    headers: { Authorization: `Bearer ${token}` }
                                                });
                                                if (res.ok) {
                                                    const blob = await res.blob();
                                                    const url = window.URL.createObjectURL(blob);
                                                    const a = document.createElement('a');
                                                    a.href = url;
                                                    a.download = `book_${book.id}.pdf`;
                                                    a.click();
                                                }
                                            }}
                                            className="flex-1 text-center px-3 py-2 text-sm font-medium text-secondary-foreground bg-secondary rounded-md hover:bg-secondary/80 transition-colors"
                                        >
                                            PDF
                                        </button>
                                    ) : null}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
