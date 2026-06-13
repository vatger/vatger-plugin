import { apiFetch, parseApiError } from "@/lib/api-client"

export type PluginToken = {
  id: string
  user: string | null
  label: string | null
  token: string
  last_used: string
}

export type AuthorizePluginErrorCode =
  | "invalid_token"
  | "already_authorized"
  | "unauthenticated"
  | "network_error"
  | "unknown"

export class AuthorizePluginError extends Error {
  readonly code: AuthorizePluginErrorCode

  constructor(code: AuthorizePluginErrorCode, message: string) {
    super(message)
    this.name = "AuthorizePluginError"
    this.code = code
  }
}

export async function authorizePluginToken(
  tokenId: string,
  label: string,
): Promise<void> {
  const response = await apiFetch(
    `/api/v1/plugin-token/authorize/${encodeURIComponent(tokenId)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ label }),
    },
  )

  if (response.status === 401) {
    throw new AuthorizePluginError(
      "unauthenticated",
      "You must be logged in to approve plugin access.",
    )
  }

  if (response.status === 403) {
    throw new AuthorizePluginError(
      "already_authorized",
      "This authorization link was already used.",
    )
  }

  if (response.status === 400) {
    const detail = await parseApiError(response)
    throw new AuthorizePluginError(
      "invalid_token",
      detail === "Invalid token"
        ? "This authorization link is invalid or has expired. Start authorization from the plugin again."
        : detail,
    )
  }

  if (!response.ok) {
    throw new AuthorizePluginError(
      "unknown",
      await parseApiError(response),
    )
  }
}

export async function fetchPluginTokens(): Promise<PluginToken[]> {
  const response = await apiFetch("/api/v1/plugin-token?scope=own")
  if (!response.ok) {
    throw new Error("Failed to load plugin tokens")
  }
  return (await response.json()) as PluginToken[]
}

export async function revokePluginToken(tokenId: string): Promise<void> {
  const response = await apiFetch(
    `/api/v1/plugin-token/${encodeURIComponent(tokenId)}`,
    { method: "DELETE" },
  )
  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }
}
