import {
  authorizePluginToken,
  AuthorizePluginError,
} from "@/app/plugin-token"
import {
  AuthorizePluginForm,
  type AuthorizePluginFormState,
} from "@/components/plugin-auth/AuthorizePluginForm"
import { isUuid } from "@/lib/uuid"
import { useState } from "react"
import { useNavigate, useParams } from "react-router"

const ERROR_MESSAGES: Record<string, string> = {
  invalid_token:
    "This authorization link is invalid or has expired. Start authorization from the plugin again.",
  already_authorized: "This authorization link was already used.",
  unauthenticated: "You must be logged in to approve plugin access.",
}

export const AuthorizePlugin = () => {
  const { id: tokenId } = useParams()
  const navigate = useNavigate()
  const [label, setLabel] = useState("")
  const [errorMessage, setErrorMessage] = useState<string>()
  const [state, setState] = useState<AuthorizePluginFormState>(() =>
    tokenId && isUuid(tokenId) ? "ready" : "invalid_link",
  )

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!tokenId || !isUuid(tokenId)) {
      setState("invalid_link")
      return
    }

    if (!label.trim()) {
      setErrorMessage("Please enter a label for this device.")
      return
    }

    setErrorMessage(undefined)
    setState("loading")

    try {
      await authorizePluginToken(tokenId, label.trim())
      setState("done")
    } catch (error) {
      if (error instanceof AuthorizePluginError) {
        if (error.code === "unauthenticated") {
          navigate(
            `/auth?next=${encodeURIComponent(window.location.pathname)}`,
          )
          return
        }
        setErrorMessage(
          ERROR_MESSAGES[error.code] ?? error.message,
        )
      } else {
        setErrorMessage("Failed to approve access. Please try again.")
      }
      setState("error")
    }
  }

  return (
    <AuthorizePluginForm
      tokenId={tokenId ?? "—"}
      label={label}
      onLabelChange={setLabel}
      state={state}
      errorMessage={errorMessage}
      onSubmit={handleSubmit}
    />
  )
}
