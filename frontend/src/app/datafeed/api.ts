import { apiFetch } from "@/lib/api-client"

export type ConnectionData = {
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

export async function fetchPilotConnection(): Promise<ConnectionData> {
  const response = await apiFetch("/api/v1/datafeed/user/pilot")
  if (!response.ok) throw new Error("Failed to load connection data")
  return (await response.json()) as ConnectionData
}
