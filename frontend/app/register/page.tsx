'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { fetchAPI } from '@/lib/api';
import Link from 'next/link';

const registerSchema = z.object({
    full_name: z.string().min(2, { message: "Name must be at least 2 characters" }),
    email: z.string().email({ message: "Invalid email address" }),
    password: z.string().min(6, { message: "Password must be at least 6 characters" }),
    confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const router = useRouter();
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<RegisterFormValues>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterFormValues) => {
        setLoading(true);
        setError(null);
        try {
            await fetchAPI('/api/v1/users/', {
                method: 'POST',
                body: JSON.stringify({
                    email: data.email,
                    password: data.password,
                    full_name: data.full_name,
                }),
            });

            // Redirect to login after successful registration
            router.push('/login');
        } catch (err: any) {
            setError(err.message || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-background p-4">
            <div className="w-full max-w-md space-y-8 rounded-2xl bg-card p-8 shadow-lg border border-border">
                <div className="text-center">
                    <h2 className="text-3xl font-bold tracking-tight text-foreground">Create an account</h2>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Get started with Fábrica de Livros
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="full_name" className="block text-sm font-medium text-foreground">
                                Full Name
                            </label>
                            <div className="mt-1">
                                <input
                                    id="full_name"
                                    type="text"
                                    autoComplete="name"
                                    className="block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary sm:text-sm"
                                    {...register('full_name')}
                                />
                                {errors.full_name && (
                                    <p className="mt-1 text-sm text-destructive">{errors.full_name.message}</p>
                                )}
                            </div>
                        </div>

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-foreground">
                                Email address
                            </label>
                            <div className="mt-1">
                                <input
                                    id="email"
                                    type="email"
                                    autoComplete="email"
                                    className="block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary sm:text-sm"
                                    {...register('email')}
                                />
                                {errors.email && (
                                    <p className="mt-1 text-sm text-destructive">{errors.email.message}</p>
                                )}
                            </div>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-foreground">
                                Password
                            </label>
                            <div className="mt-1">
                                <input
                                    id="password"
                                    type="password"
                                    autoComplete="new-password"
                                    className="block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary sm:text-sm"
                                    {...register('password')}
                                />
                                {errors.password && (
                                    <p className="mt-1 text-sm text-destructive">{errors.password.message}</p>
                                )}
                            </div>
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-foreground">
                                Confirm Password
                            </label>
                            <div className="mt-1">
                                <input
                                    id="confirmPassword"
                                    type="password"
                                    autoComplete="new-password"
                                    className="block w-full rounded-md border border-input bg-background px-3 py-2 text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary sm:text-sm"
                                    {...register('confirmPassword')}
                                />
                                {errors.confirmPassword && (
                                    <p className="mt-1 text-sm text-destructive">{errors.confirmPassword.message}</p>
                                )}
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div className="rounded-md bg-destructive/10 p-4">
                            <div className="flex">
                                <div className="ml-3">
                                    <h3 className="text-sm font-medium text-destructive">{error}</h3>
                                </div>
                            </div>
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex w-full justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {loading ? 'Creating account...' : 'Sign up'}
                        </button>
                    </div>

                    <div className="text-center text-sm">
                        <p className="text-muted-foreground">
                            Already have an account?{' '}
                            <Link href="/login" className="font-medium text-primary hover:text-primary/80">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
}
