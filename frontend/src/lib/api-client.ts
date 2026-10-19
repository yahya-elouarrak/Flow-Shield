import { ApiError } from "./types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

export async function fetchApi<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...init } = options;
  
  let url = `${API_BASE_URL}${path}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  try {
    const response = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = "API request failed";
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || errorMessage;
      } catch {
        // Fallback to text or status text
        errorMessage = errorText || response.statusText;
      }
      throw { message: errorMessage, status: response.status } as ApiError;
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json() as T;
  } catch (error) {
    // If it's already an ApiError (from our throw above), rethrow it
    if (typeof error === "object" && error !== null && "status" in error) {
      throw error;
    }
    
    // Otherwise it's a network error (e.g. backend offline)
    console.error("Network Error:", error);
    throw { message: "Cannot connect to FlowShield backend. Is it running?" } as ApiError;
  }
}
