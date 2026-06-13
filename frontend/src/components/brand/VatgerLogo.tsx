import { useResolvedTheme } from "@/components/theme-provider"
import { cn } from "@/lib/utils"

export function VatgerLogo({ className }: { className?: string }) {
  const theme = useResolvedTheme()

  return (
    <img
      className={cn("h-10", className)}
      alt="VATGER"
      src={
        theme === "dark" ? "/vatger_logo_light.svg" : "/vatger_logo_dark.svg"
      }
    />
  )
}
