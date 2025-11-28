const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://voidtruth.onrender.com';

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || error.message || 'API Error');
  }

  return res.json();
}
