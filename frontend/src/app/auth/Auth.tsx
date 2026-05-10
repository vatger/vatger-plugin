import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router"
import { Login } from "@/views/Login"
import {
  AuthError,
  type AuthErrorCode,
  authorizeToken,
  fetchCurrentUser,
} from "./api"
import { useAppDispatch } from "./hooks"
import { setUser } from "./slice"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useTheme } from "@/components/theme-provider"

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
  const navigate = useNavigate()

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
        navigate("/")
      } catch {
        // not logged in, stay on login page
      }
    }

    resolveSession()
  }, [dispatch, navigate])

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

  return (
    <Login
      error={error ? ERROR_MESSAGES[error] : undefined}
      loading={loading}
      onClick={startLogin}
    />
  )
}

type State = "start" | "load" | "done" | "error"

export const AuthorizePluginToken = () => {
  const { id: tokenId } = useParams()
  const [label, setLabel] = useState("")
  const [state, setState] = useState<State>("start")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!tokenId) return setState("error")

    try {
      setState("load")
      await authorizeToken(tokenId, label)
      setState("done")
    } catch (err) {
      console.error(err)
      setState("error")
    }
  }

  return (
    <div className="flex size-full min-h-screen items-center justify-center text-center">
      <Card>
        <img
          className="p-12 pb-4"
          src={
            useTheme().theme === "dark"
              ? "/vatger_logo_light.svg"
              : "/vatger_logo_dark.svg"
          }
        />
        <p className="text-center">
          A EuroScope vatger-plugin requested access in your name.
        </p>
        {state === "done" ? (
          <p>The access was approved. This tab can be closed.</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mx-12 flex flex-col items-center gap-3">
              <div className="flex w-full flex-col gap-2">
                <Label htmlFor="inputLabel">Label</Label>
                <Input
                  id="inputLabel"
                  onChange={(e) => setLabel(e.target.value)}
                  placeholder="My personal computer"
                  value={label}
                />
              </div>

              {state === "error" && (
                <p className="text-center text-red-600">
                  <strong>Error</strong>: Failed to approve the access.
                </p>
              )}

              <p className="text-center text-sm text-gray-500">
                Token: {tokenId}
              </p>

              <Button
                className="px-8"
                disabled={state === "load"}
                type="submit"
              >
                Approve
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  )
}
