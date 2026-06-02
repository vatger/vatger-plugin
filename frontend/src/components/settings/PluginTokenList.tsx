import {
  fetchPluginTokens,
  revokePluginToken,
  type PluginToken,
} from "@/app/plugin-token"
import { SkeletonLine } from "@/components/efb/efb-ui"
import { formatLastUsed, maskToken } from "@/lib/format"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Loader2, Trash2 } from "lucide-react"
import { useState } from "react"

export const PLUGIN_TOKENS_KEY = ["pluginTokens"] as const

export function PluginTokenList() {
  const queryClient = useQueryClient()
  const [revokeError, setRevokeError] = useState<string | null>(null)

  const {
    data: tokens = [],
    isPending,
    isError,
  } = useQuery({
    queryKey: PLUGIN_TOKENS_KEY,
    queryFn: fetchPluginTokens,
  })

  const revoke = useMutation({
    mutationFn: revokePluginToken,
    onSuccess: () => {
      setRevokeError(null)
      void queryClient.invalidateQueries({ queryKey: PLUGIN_TOKENS_KEY })
    },
    onError: (error: Error) => {
      setRevokeError(error.message)
    },
  })

  const handleRevoke = (token: PluginToken) => {
    const label = token.label?.trim() || "this plugin token"
    if (
      !window.confirm(
        `Revoke access for "${label}"? The plugin will need to be authorized again.`,
      )
    ) {
      return
    }
    revoke.mutate(token.id)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Plugin tokens</CardTitle>
        <CardDescription>
          EuroScope and other plugins authorized with your account
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {revokeError && (
          <p className="text-sm text-destructive">{revokeError}</p>
        )}

        {isPending ? (
          <div className="space-y-2">
            <SkeletonLine />
            <SkeletonLine w="w-4/5" />
          </div>
        ) : isError ? (
          <p className="text-sm text-muted-foreground">
            Could not load plugin tokens.
          </p>
        ) : tokens.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No active plugin tokens. Authorize a plugin from EuroScope to create
            one.
          </p>
        ) : (
          <ul className="space-y-2">
            {tokens.map((token) => (
              <li
                key={token.id}
                className="flex items-start justify-between gap-3 rounded-lg border bg-muted/15 p-3"
              >
                <div className="min-w-0 space-y-1">
                  <p className="font-medium">
                    {token.label?.trim() || "Unlabeled device"}
                  </p>
                  <p className="font-mono text-xs text-muted-foreground">
                    {maskToken(token.token)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Last used {formatLastUsed(token.last_used)}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={revoke.isPending && revoke.variables === token.id}
                  onClick={() => handleRevoke(token)}
                >
                  {revoke.isPending && revoke.variables === token.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                  Revoke
                </Button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
