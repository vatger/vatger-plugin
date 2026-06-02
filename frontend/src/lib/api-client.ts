export async function parseApiError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string | unknown }
    if (typeof data.detail === "string") return data.detail
  } catch {
    /* response may not be JSON */
  }
  return "Something went wrong. Please try again."
}

export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  return fetch(input, {
    credentials: "include",
    ...init,
    headers: {
      ...init?.headers,
    },
  })
}
