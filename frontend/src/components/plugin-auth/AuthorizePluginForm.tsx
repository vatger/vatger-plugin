import { VatgerLogo } from "@/components/brand/VatgerLogo"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2 } from "lucide-react"

export type AuthorizePluginFormState =
  | "ready"
  | "loading"
  | "done"
  | "invalid_link"
  | "error"

type AuthorizePluginFormProps = {
  tokenId: string
  label: string
  onLabelChange: (label: string) => void
  state: AuthorizePluginFormState
  errorMessage?: string
  onSubmit: (event: React.FormEvent) => void
}

export function AuthorizePluginForm({
  tokenId,
  label,
  onLabelChange,
  state,
  errorMessage,
  onSubmit,
}: AuthorizePluginFormProps) {
  const disabled = state === "loading" || state === "invalid_link" || state === "done"

  return (
    <div className="flex min-h-screen w-full items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <div className="flex flex-col items-center gap-4 p-8">
          <VatgerLogo className="h-10" />

          <div className="space-y-1 text-center">
            <h1 className="text-xl font-semibold">Authorize plugin</h1>
            <p className="text-sm text-muted-foreground">
              A VATGER plugin requested access to your account.
            </p>
          </div>

          {state === "done" ? (
            <p className="text-center text-sm">
              Access approved. You can close this tab and return to the plugin.
            </p>
          ) : state === "invalid_link" ? (
            <div className="space-y-2 text-center text-sm text-destructive">
              <p className="font-medium">This authorization link is not valid.</p>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="flex w-full flex-col gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="plugin-label">Device label</Label>
                <Input
                  id="plugin-label"
                  value={label}
                  onChange={(e) => onLabelChange(e.target.value)}
                  placeholder="My personal computer"
                  disabled={disabled}
                  required
                />
              </div>

              {errorMessage && (
                <p className="text-center text-sm text-destructive" role="alert">
                  {errorMessage}
                </p>
              )}

              <p className="text-center font-mono text-xs text-muted-foreground">
                {tokenId}
              </p>

              <Button type="submit" className="w-full" disabled={disabled}>
                {state === "loading" ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Approving…
                  </>
                ) : (
                  "Approve access"
                )}
              </Button>
            </form>
          )}
        </div>
      </Card>
    </div>
  )
}
