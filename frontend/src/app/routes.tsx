import { createBrowserRouter, Navigate } from "react-router"
import { Auth, RequireAuth, AuthorizePluginToken } from "./auth"

const router = createBrowserRouter([
	{
		path: "/*",
		element: <Navigate to="/auth" replace />
	},
	{
		path: "/auth",
		element: <Auth />,
	},
	{
		path: "/authorize-plugin/:id",
		element: (
			<RequireAuth>
				<AuthorizePluginToken />
			</RequireAuth>
		),
	},
])

export default router
