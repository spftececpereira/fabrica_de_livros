const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
    token?: string;
}

export async function fetchAPI(endpoint: string, options: FetchOptions = {}) {
    const { token, headers, ...rest } = options;

    const defaultHeaders: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(headers as Record<string, string>),
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
        headers: defaultHeaders,
        ...rest,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'An error occurred');
    }

    // Handle empty responses (e.g. 204)
    if (response.status === 204) {
        return null;
    }

    return response.json();
}
