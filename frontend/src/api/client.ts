const API_BASE_URL =
  import.meta.env.VITE_API_URL ??
  "http://localhost:8000";

export async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    },
  );

  if (!response.ok) {
    let message =
      `API request failed: ${response.status}`;

    try {
      const body = await response.json();

      if (
        body &&
        typeof body.detail === "string"
      ) {
        message = body.detail;
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function apiGet<T>(
  path: string,
): Promise<T> {
  return apiRequest<T>(path, {
    method: "GET",
  });
}

export async function apiPost<T>(
  path: string,
  body: unknown,
): Promise<T> {
  return apiRequest<T>(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
