const AUTH_BASE = "/api/v1/auth"

export interface UserDto {
	cid: string
	access: boolean
	admin: boolean
}

export async function exchangeCode(code: string): Promise<void> {
	const res = await fetch(AUTH_BASE, {
		method: "POST",
		credentials: "include",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ code }),
	})

	if (res.status === 403) throw new AuthError("access_denied")
	if (!res.ok) throw new AuthError("auth_failed")
}

export async function fetchCurrentUser(): Promise<UserDto> {
	const res = await fetch(`${AUTH_BASE}/user`, { credentials: "include" })

	if (res.status === 403) throw new AuthError("access_denied")
	if (res.status === 401) throw new AuthError("unauthenticated")
	if (!res.ok) throw new AuthError("auth_failed")

	return res.json()
}

export async function refreshTokens(): Promise<void> {
	const res = await fetch(`${AUTH_BASE}/refresh`, {
		method: "POST",
		credentials: "include",
	})

	if (!res.ok) throw new AuthError("refresh_failed")
}

export async function authorizeToken(
	tokenId: string,
	label: string,
): Promise<void> {
	const res = await fetch(`/api/v1/plugin-token/authorize/${tokenId}`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ label }),
	})

	if (!res.ok) throw new Error(`Request failed: ${res.status}`)
}

export async function logout(): Promise<void> {
	await fetch(`${AUTH_BASE}/logout`, {
		method: "POST",
		credentials: "include",
	})
}

export type AuthErrorCode =
	| "access_denied"
	| "auth_failed"
	| "unauthenticated"
	| "refresh_failed"
	| "network_error"

export class AuthError extends Error {
	constructor(public readonly code: AuthErrorCode) {
		super(code)
		this.name = "AuthError"
	}
}
