import { createBrowserRouter, Navigate } from "react-router"
import { Auth, RequireAuth } from "./auth"
import { EfbSettingsProvider } from "./efb"
import { AuthorizePlugin } from "@/views/AuthorizePlugin"
import { Efb } from "@/views/Efb"

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <RequireAuth>
        <EfbSettingsProvider>
          <Efb />
        </EfbSettingsProvider>
      </RequireAuth>
    ),
  },
  {
    path: "/auth",
    element: <Auth />,
  },
  {
    path: "/authorize-plugin/:id",
    element: (
      <RequireAuth>
        <AuthorizePlugin />
      </RequireAuth>
    ),
  },
  {
    path: "/settings",
    element: <Navigate to="/" replace />,
  },
  {
    path: "/*",
    element: <Navigate to="/auth" replace />,
  },
])

export default router
