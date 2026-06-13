import { FeedbackBanner, Pill, SkeletonLine } from "@/components/efb/efb-ui"
import type { RequestType, SilentRequest } from "@/app/silent-request"
import { formatRequestType, formatRequestedAt } from "@/lib/format"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Toggle } from "@/components/ui/toggle"
import { Loader2, Road, Trash2, Van } from "lucide-react"

type SilentRequestsCardProps = {
  isOnline: boolean
  selectedType: RequestType | undefined
  onSelectType: (type: RequestType | undefined) => void
  pendingRequest: SilentRequest | null | undefined
  pendingLoading: boolean
  pendingFetching: boolean
  feedback: { variant: "success" | "error"; message: string } | null
  canSendRequest: boolean
  sendPending: boolean
  cancelPending: boolean
  pendingSameType: boolean
  onSend: () => void
  onCancel: () => void
}

export function SilentRequestsCard({
  isOnline,
  selectedType,
  onSelectType,
  pendingRequest,
  pendingLoading,
  pendingFetching,
  feedback,
  canSendRequest,
  sendPending,
  cancelPending,
  pendingSameType,
  onSend,
  onCancel,
}: SilentRequestsCardProps) {
  const hasPending = !!pendingRequest

  return (
    <Card className="shrink-0">
      <CardHeader className="space-y-1 pb-3">
        <CardTitle>Silent requests</CardTitle>
        <CardDescription>
          Request pushback or taxi without blocking the frequency
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {feedback && (
          <FeedbackBanner
            variant={feedback.variant}
            message={feedback.message}
          />
        )}

        {pendingLoading ? (
          <div className="rounded-lg border bg-muted/20 p-3">
            <SkeletonLine w="w-2/3" />
          </div>
        ) : hasPending ? (
          <div className="rounded-lg border border-sky-500/30 bg-sky-500/10 p-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <Pill variant="info">Pending</Pill>
                  {(pendingFetching || cancelPending) && (
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                  )}
                </div>
                <p className="mt-2 text-sm font-semibold">
                  {formatRequestType(pendingRequest.type)} at{" "}
                  {pendingRequest.departure_icao}
                </p>
                <p className="text-xs text-muted-foreground">
                  Requested {formatRequestedAt(pendingRequest.requested_at)}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                disabled={cancelPending}
                onClick={onCancel}
                aria-label="Cancel pending request"
              >
                <Trash2 className="h-4 w-4" />
                Cancel
              </Button>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              ATC can see your request. Select another type below to change it,
              or cancel to withdraw.
            </p>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">No active request.</p>
        )}

        <div className="flex flex-wrap gap-2">
          <Toggle
            pressed={selectedType === "PUSHBACK"}
            onPressedChange={(pressed) =>
              onSelectType(pressed ? "PUSHBACK" : undefined)
            }
            size="lg"
            variant="outline"
            disabled={!isOnline || sendPending}
          >
            <Van />
            Pushback
          </Toggle>
          <Toggle
            pressed={selectedType === "TAXI"}
            onPressedChange={(pressed) =>
              onSelectType(pressed ? "TAXI" : undefined)
            }
            size="lg"
            variant="outline"
            disabled={!isOnline || sendPending}
          >
            <Road />
            Taxi
          </Toggle>
        </div>

        <Button
          disabled={!canSendRequest}
          variant="outline"
          className="w-full"
          onClick={onSend}
        >
          {sendPending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Sending…
            </>
          ) : selectedType ? (
            `Send ${formatRequestType(selectedType)} request`
          ) : (
            "Select request type"
          )}
        </Button>

        {!isOnline && (
          <p className="text-xs text-muted-foreground">
            Connect to VATSIM as a pilot to send requests.
          </p>
        )}
        {pendingSameType && selectedType && (
          <p className="text-xs text-muted-foreground">
            You already have a pending {formatRequestType(selectedType)}{" "}
            request.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
