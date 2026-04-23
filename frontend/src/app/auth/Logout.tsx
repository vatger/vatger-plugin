import { useEffect } from "react"
import { useNavigate } from "react-router"
import { logout } from "./api"
import { useAppDispatch } from "./hooks"
import { clearUser } from "./slice"
import { Login } from "@/views/Login"

export const Logout = () => {
	const dispatch = useAppDispatch()
	const navigate = useNavigate()

	useEffect(() => {
		logout().finally(() => {
			dispatch(clearUser())
			navigate("/auth")
		})
	}, [dispatch, navigate])

	return (
		<Login loading onClick={() => undefined} />
	)
}
