export function formatZuluTime(date = new Date()) {
  const hh = String(date.getUTCHours()).padStart(2, "0")
  const mm = String(date.getUTCMinutes()).padStart(2, "0")
  return `${hh}${mm}Z`
}

export function formatRequestType(type: "TAXI" | "PUSHBACK") {
  return type.charAt(0) + type.slice(1).toLowerCase()
}

export function formatRequestedAt(iso: string) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return "—"
  const hh = String(date.getUTCHours()).padStart(2, "0")
  const mm = String(date.getUTCMinutes()).padStart(2, "0")
  return `${hh}:${mm}Z`
}

export function formatLastUsed(iso: string) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return "Never"
  return date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  })
}

export function maskToken(token: string) {
  if (token.length <= 8) return "••••••••"
  return `••••${token.slice(-4)}`
}
