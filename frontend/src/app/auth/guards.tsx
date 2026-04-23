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

		const resolveSession = async () => {
			try {
				const userData = await fetchCurrentUser()
				dispatch(setUser(userData))
			} catch (e) {
				if (!(e instanceof AuthError)) {
					dispatch(clearUser())
					navigate("/auth")
					return
				}

				if (e.code !== "unauthenticated") {
					dispatch(clearUser())
					navigate("/auth")
					return
				}

				try {
					await refreshTokens()
					const userData = await fetchCurrentUser()
					dispatch(setUser(userData))
				} catch {
					dispatch(clearUser())
					navigate("/auth")
				}
			}
		}

		resolveSession()
	}, [user, dispatch, navigate])

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
