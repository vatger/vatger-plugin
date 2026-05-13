import { useEffect } from "react"
import { useNavigate } from "react-router"
import { AuthError, fetchCurrentUser, refreshTokens } from "./api"
import { useAppDispatch, useAppSelector } from "./hooks"
import { clearUser, selectUser, setUser } from "./slice"

export const RequireAuth = ({ children }: { children: React.JSX.Element }) => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const user = useAppSelector(selectUser)

  useEffect(() => {
    if (user) return

    const next = window.location.pathname + window.location.search

    const resolveSession = async () => {
      try {
        const userData = await fetchCurrentUser()
        dispatch(setUser(userData))
      } catch (e) {
        if (!(e instanceof AuthError)) {
          dispatch(clearUser())
          navigate(`/auth?next=${encodeURIComponent(next)}`)
          return
        }

        if (e.code !== "unauthenticated") {
          dispatch(clearUser())
          navigate(`/auth?next=${encodeURIComponent(next)}`)
          return
        }

        try {
          await refreshTokens()
          const userData = await fetchCurrentUser()
          dispatch(setUser(userData))
        } catch {
          dispatch(clearUser())
          navigate(`/auth?next=${encodeURIComponent(next)}`)
        }
      }
    }

    resolveSession()
  }, [])

  if (!user) return null

  return children
}

export const RequireAdmin = ({ children }: { children: React.JSX.Element }) => {
  const user = useAppSelector(selectUser)
  const navigate = useNavigate()

  useEffect(() => {
    if (user && !user.admin) navigate("/")
  }, [user, navigate])

  return children
}
