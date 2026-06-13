import { ComingSoonPanel } from "@/components/dashboard/ComingSoonPanel"
import { FlightOverviewCard } from "@/components/dashboard/FlightOverviewCard"
import { SilentRequestsCard } from "@/components/dashboard/SilentRequestsCard"
import type { ConnectionData } from "@/app/datafeed"
import type { RequestType, SilentRequest } from "@/app/silent-request"

type DashboardGridProps = {
  connection: ConnectionData | undefined
  connectionPending: boolean
  connectionError: boolean
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

export function DashboardGrid(props: DashboardGridProps) {
  return (
    <div className="grid auto-rows-min grid-cols-12 content-start items-start gap-3 min-[1400px]:h-full min-[1400px]:overflow-y-auto">
      <div className="col-span-12 self-start min-[1400px]:col-span-5">
        <FlightOverviewCard
          isPending={props.connectionPending}
          isError={props.connectionError}
          connection={props.connection}
        />
      </div>

      <div className="col-span-12 flex flex-col gap-3 self-start min-[1400px]:col-span-7">
        <SilentRequestsCard
          isOnline={props.isOnline}
          selectedType={props.selectedType}
          onSelectType={props.onSelectType}
          pendingRequest={props.pendingRequest}
          pendingLoading={props.pendingLoading}
          pendingFetching={props.pendingFetching}
          feedback={props.feedback}
          canSendRequest={props.canSendRequest}
          sendPending={props.sendPending}
          cancelPending={props.cancelPending}
          pendingSameType={props.pendingSameType}
          onSend={props.onSend}
          onCancel={props.onCancel}
        />
        <ComingSoonPanel />
      </div>
    </div>
  )
}
