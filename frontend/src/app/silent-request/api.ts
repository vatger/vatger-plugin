import { apiFetch, parseApiError } from "@/lib/api-client"

export type SilentRequest = {
  callsign: string
  departure_icao: string
  type: "TAXI" | "PUSHBACK"
  requested_at: string
}

export type RequestType = SilentRequest["type"]

export async function fetchSilentRequest(): Promise<SilentRequest | null> {
  const response = await apiFetch("/api/v1/silent-request")
  if (response.status === 404) return null
  if (!response.ok) throw new Error("Failed to load silent request")
  return (await response.json()) as SilentRequest
}

export async function createSilentRequest(type: RequestType): Promise<void> {
  const response = await apiFetch("/api/v1/silent-request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type }),
  })
  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }
}

export async function deleteSilentRequest(): Promise<void> {
  const response = await apiFetch("/api/v1/silent-request", {
    method: "DELETE",
  })
  if (!response.ok) {
    throw new Error(await parseApiError(response))
  }
}
