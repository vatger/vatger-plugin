import { useResolvedTheme } from "@/components/theme-provider"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Toggle } from "@/components/ui/toggle"
import { Loader2, Road, Van } from "lucide-react"
import { useState } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"

type ConnectionData = {
  cid: number
  callsign: string
  latitude: number
  longitude: number
  altitude: number
  groundspeed: number
  heading: number
  qnh_i_hg: number
  qnh_mb: number
  flight_plan: {
    flight_rules: string
    aircraft: string
    aircraft_faa: string
    departure: string
    arrival: string
    alternate: string
    deptime: string
    enroute_time: string
    fuel_time: string
    remarks: string
    route: string
    revision_id: number
  }
  logon_time: string
  last_updated: string
}

export const Dashboard = () => {
  const theme = useResolvedTheme()
  const [selectedType, setSelectedType] = useState<"PUSHBACK" | "TAXI">()

  const {
    data: connectionData,
    isError,
    isPending,
  } = useQuery({
    queryKey: ["connectionData"],
    queryFn: async (): Promise<ConnectionData> => {
      const response = await fetch(`/api/v1/datafeed/user/pilot`)
      return (await response.json()) as ConnectionData
    },
    refetchInterval: 10000,
  })

  const sendRequest = useMutation({
    mutationFn: async (type: string) => {
      const response = await fetch("/api/v1/silent-request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ type })
      })
      return (await response.json())
    }
  })

  const isOnline = connectionData !== null
  const canSendRequest = selectedType && isOnline

  return (
    <div className="flex size-full min-h-screen items-center justify-center">
      <Card>
        <img
          className="p-12 pb-4"
          src={
            theme === "dark"
              ? "/vatger_logo_light.svg"
              : "/vatger_logo_dark.svg"
          }
        />
        {!isPending && isError && "An error occurred"}

        {isPending && (
          <Card className="m-4 flex items-center justify-center">
            <Loader2 className="animate-spin" />
            <i>Starting engines...</i>
          </Card>
        )}

        {isOnline && !isPending && (
          <>
            <Card className="mx-4">
              <CardHeader className="flex justify-between">
                <div className="w-1/2">
                  <p className="text-xs text-muted-foreground">Callsign</p>
                  <h1 className="text-3xl">{connectionData?.callsign}</h1>
                </div>

                <div className="w-1/2">
                  <p className="text-xs text-muted-foreground">Aircraft</p>
                  <h1 className="text-3xl">{connectionData?.flight_plan.aircraft}</h1>
                </div>
              </CardHeader>
            </Card>
            <Card className="mx-4 mb-4">
              <CardHeader>
                <CardTitle>Silent Request</CardTitle>
                <CardDescription>
                  Send silent requests to avoid blocking out other pilots on
                  highly occupied frequencies
                </CardDescription>
              </CardHeader>
              <CardContent className="flex gap-2">
                <Toggle
                  pressed={selectedType === "PUSHBACK"}
                  onPressedChange={() => setSelectedType("PUSHBACK")}
                  size={"lg"}
                  variant={"outline"}
                >
                  <Van />
                  Pushback
                </Toggle>
                <Toggle
                  pressed={selectedType === "TAXI"}
                  onPressedChange={() => setSelectedType("TAXI")}
                  size={"lg"}
                  variant={"outline"}
                >
                  <Road />
                  Taxi
                </Toggle>
              </CardContent>
              <CardFooter>
                <Button
                  disabled={!canSendRequest || sendRequest.isPending}
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => sendRequest.mutate(selectedType!)}
                >
                    {selectedType && "Silently"} Request <span>{selectedType && selectedType?.charAt(0) + selectedType?.slice(1).toLowerCase()}</span>
                </Button>
              </CardFooter>
            </Card>
          </>
        )}
      </Card>
    </div>
  )
}
