import { Pill } from "@/components/efb/efb-ui"
import { Clock, Plane, SignalHigh } from "lucide-react"

export function ConnectionStatusPills({
  isOnline,
  connectionPending,
  zuluTime,
}: {
  isOnline: boolean
  connectionPending: boolean
  zuluTime: string
}) {
  return (
    <>
      <Pill variant={isOnline ? "success" : "warning"}>
        <SignalHigh className="h-3.5 w-3.5" />
        {isOnline
          ? "Connected"
          : connectionPending
            ? "Connecting…"
            : "Offline"}
      </Pill>
      <Pill>
        <Clock className="h-3.5 w-3.5" />
        {zuluTime}
      </Pill>
    </>
  )
}

export function CallsignPill({ callsign }: { callsign: string }) {
  return (
    <Pill>
      <Plane className="h-3.5 w-3.5" />
      {callsign}
    </Pill>
  )
}
