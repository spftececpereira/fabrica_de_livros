'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { BookOpen, LogOut, Plus, User } from 'lucide-react';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            router.push('/login');
        } else {
            setIsAuthenticated(true);
        }
    }, [router]);

    const handleLogout = () => {
        localStorage.removeItem('token');
        router.push('/login');
    };

    if (!isAuthenticated) {
        return null; // Or a loading spinner
    }

    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <aside className="w-64 border-r border-border bg-card hidden md:flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
                        <BookOpen className="h-8 w-8" />
                        Fábrica
                    </h1>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    <Link
                        href="/dashboard"
                        className="flex items-center gap-3 px-4 py-3 text-foreground hover:bg-accent hover:text-accent-foreground rounded-lg transition-colors"
                    >
                        <BookOpen className="h-5 w-5" />
                        My Books
                    </Link>
                    <Link
                        href="/dashboard/create"
                        className="flex items-center gap-3 px-4 py-3 text-foreground hover:bg-accent hover:text-accent-foreground rounded-lg transition-colors"
                    >
                        <Plus className="h-5 w-5" />
                        Create Book
                    </Link>
                    <Link
                        href="/dashboard/profile"
                        className="flex items-center gap-3 px-4 py-3 text-foreground hover:bg-accent hover:text-accent-foreground rounded-lg transition-colors"
                    >
                        <User className="h-5 w-5" />
                        Profile
                    </Link>
                </nav>

                <div className="p-4 border-t border-border">
                    <button
                        onClick={handleLogout}
                        className="flex w-full items-center gap-3 px-4 py-3 text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
                    >
                        <LogOut className="h-5 w-5" />
                        Sign Out
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <header className="h-16 border-b border-border bg-card flex items-center px-8 md:hidden">
                    <h1 className="text-xl font-bold text-primary">Fábrica de Livros</h1>
                </header>
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
