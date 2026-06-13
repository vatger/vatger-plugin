import { formatZuluTime } from "@/lib/format"
import { useEffect, useState } from "react"

export function useZuluClock(intervalMs = 30_000) {
  const [zuluTime, setZuluTime] = useState(formatZuluTime)

  useEffect(() => {
    const tick = () => setZuluTime(formatZuluTime())
    const id = window.setInterval(tick, intervalMs)
    return () => window.clearInterval(id)
  }, [intervalMs])

  return zuluTime
}
