import { useEffect, useState } from "react"
import { Navigate } from "react-router"
import { Login } from "@/views/Login"
import {
  AuthError,
  type AuthErrorCode,
  fetchCurrentUser,
} from "./api"
import { useAppDispatch, useAppSelector } from "./hooks"
import { selectUser, setUser } from "./slice"
const ERROR_MESSAGES: Record<AuthErrorCode, string> = {
  access_denied: "Your account does not have access to this system.",
  auth_failed: "Login failed. Please try again.",
  unauthenticated: "Your session has expired. Please log in again.",
  refresh_failed: "Could not refresh your session. Please log in again.",
  network_error: "Could not reach the server. Please try again.",
}

export const Auth = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<AuthErrorCode | null>(null)
  const dispatch = useAppDispatch()
  const user = useAppSelector(selectUser)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const errorParam = params.get("error") as AuthErrorCode | null

    if (errorParam) {
      setError(errorParam)
      return
    }

    const resolveSession = async () => {
      try {
        const user = await fetchCurrentUser()
        dispatch(setUser(user))
      } catch {
        // not logged in
      }
    }

    if (user) return

    resolveSession()
  }, [])

  const startLogin = () => {
    setLoading(true)
    setError(null)

    const params = new URLSearchParams(window.location.search)
    const next = params.get("next")

    const authUrl = next
      ? `/api/v1/auth?state=${encodeURIComponent(next)}`
      : "/api/v1/auth"

    try {
      window.location.replace(
        `${window.location.protocol}//${window.location.host}${authUrl}`
      )
    } catch (e) {
      setError(e instanceof AuthError ? e.code : "network_error")
      setLoading(false)
    }
  }

  if (user) return <Navigate to="/" replace />

  return (
    <Login
      error={error ? ERROR_MESSAGES[error] : undefined}
      loading={loading}
      onClick={startLogin}
    />
  )
}

