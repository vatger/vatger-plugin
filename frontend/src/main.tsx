import { store } from "@/app/auth/store"
import router from "@/app/routes"
import React, { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { Provider } from "react-redux"
import { RouterProvider } from "react-router"
import "./index.css"
import { ThemeProvider } from "@/components/theme-provider"
import { QueryClientProvider, QueryClient } from "@tanstack/react-query"

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Provider store={store}>
      <StrictMode>
        <ThemeProvider>
          <QueryClientProvider client={new QueryClient()}>
            <RouterProvider router={router} />
          </QueryClientProvider>
        </ThemeProvider>
      </StrictMode>
    </Provider>
  </React.StrictMode>
)
