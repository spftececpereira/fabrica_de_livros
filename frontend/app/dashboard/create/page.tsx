'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { fetchAPI } from '@/lib/api';

const createBookSchema = z.object({
    title: z.string().min(3, "Title must be at least 3 characters"),
    theme: z.string().min(3, "Theme must be at least 3 characters"),
    style: z.string().min(3, "Style must be at least 3 characters"),
});

type CreateBookValues = z.infer<typeof createBookSchema>;

export default function CreateBookPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<CreateBookValues>({
        resolver: zodResolver(createBookSchema),
    });

    const onSubmit = async (data: CreateBookValues) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) throw new Error("Not authenticated");

            await fetchAPI('/api/v1/books/', {
                method: 'POST',
                token,
                body: JSON.stringify(data),
            });

            router.push('/dashboard');
        } catch (error) {
            console.error('Failed to create book:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight mb-8">Create New Book</h2>

            <div className="bg-card p-8 rounded-2xl border border-border shadow-sm">
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">Book Title</label>
                        <input
                            {...register('title')}
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                            placeholder="e.g., The Space Explorer"
                        />
                        {errors.title && <p className="text-destructive text-sm mt-1">{errors.title.message}</p>}
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Theme / Topic</label>
                        <input
                            {...register('theme')}
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                            placeholder="e.g., Space, Dinosaurs, Friendship"
                        />
                        {errors.theme && <p className="text-destructive text-sm mt-1">{errors.theme.message}</p>}
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Art Style</label>
                        <select
                            {...register('style')}
                            className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                        >
                            <option value="Cartoon">Cartoon</option>
                            <option value="Realistic">Realistic</option>
                            <option value="Watercolor">Watercolor</option>
                            <option value="Pixel Art">Pixel Art</option>
                            <option value="3D Render">3D Render</option>
                        </select>
                        {errors.style && <p className="text-destructive text-sm mt-1">{errors.style.message}</p>}
                    </div>

                    <div className="pt-4">
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full btn-gradient text-white font-bold py-3 px-6 rounded-lg shadow-lg transform transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creating Magic...' : 'Generate Book'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
