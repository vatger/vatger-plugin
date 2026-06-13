import { SkeletonLine } from "@/components/efb/efb-ui"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { ConnectionData } from "@/app/datafeed"
import { AlertTriangle } from "lucide-react"

type FlightOverviewCardProps = {
  isPending: boolean
  isError: boolean
  connection: ConnectionData | undefined
}

export function FlightOverviewCard({
  isPending,
  isError,
  connection,
}: FlightOverviewCardProps) {
  const callsign = connection?.callsign ?? "—"
  const aircraft = connection?.flight_plan?.aircraft ?? "—"
  const dep = connection?.flight_plan?.departure ?? "—"
  const arr = connection?.flight_plan?.arrival ?? "—"
  const route = connection?.flight_plan?.route ?? ""

  return (
    <Card className="border-primary/15 bg-primary/[0.02]">
      <CardHeader className="pb-2">
        <CardTitle>Flight overview</CardTitle>
        <CardDescription>Live data from your VATSIM connection</CardDescription>
      </CardHeader>
      <CardContent>
        {isPending ? (
          <div className="space-y-3 py-4">
            <SkeletonLine w="w-2/3" />
            <SkeletonLine w="w-1/2" />
            <SkeletonLine w="w-3/4" />
          </div>
        ) : isError ? (
          <div className="flex items-start gap-2 text-sm text-muted-foreground">
            <AlertTriangle className="mt-0.5 h-4 w-4 text-amber-500" />
            <span>Couldn’t load connection data.</span>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">Callsign</p>
                <p className="text-2xl font-bold tracking-tight min-[1400px]:text-3xl">
                  {callsign}
                </p>
              </div>
              <div className="text-right min-[1400px]:text-left">
                <p className="text-xs text-muted-foreground">Aircraft</p>
                <p className="text-xl font-semibold min-[1400px]:text-2xl">
                  {aircraft}
                </p>
              </div>
            </div>

            <div>
              <p className="text-xs text-muted-foreground">Route</p>
              <p className="text-xl font-semibold tracking-tight min-[1400px]:text-2xl">
                {dep}
                <span className="mx-1.5 text-muted-foreground">→</span>
                {arr}
              </p>
            </div>

            {route ? (
              <div>
                <p className="text-xs text-muted-foreground">Filed route</p>
                <p
                  className="mt-0.5 line-clamp-2 font-mono text-xs leading-relaxed text-muted-foreground"
                  title={route}
                >
                  {route}
                </p>
              </div>
            ) : null}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
