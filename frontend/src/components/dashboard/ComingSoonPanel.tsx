import { Pill } from "@/components/efb/efb-ui"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const COMING_SOON = [
  "Stand assignment (ATC)",
  "TOBT display",
  "PDC / DCL management",
  "ECFMP measures",
] as const

export function ComingSoonPanel() {
  return (
    <Card className="border-dashed opacity-80">
      <CardHeader className="space-y-1 pb-2">
        <CardTitle className="text-base">More modules</CardTitle>
        <CardDescription>Planned EFB capabilities</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {COMING_SOON.map((label) => (
          <div
            key={label}
            className="flex items-center justify-between rounded-lg border border-dashed bg-muted/15 px-3 py-2 text-sm"
          >
            <span className="text-muted-foreground">{label}</span>
            <Pill>Coming soon</Pill>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
