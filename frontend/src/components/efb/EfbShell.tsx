import { VatgerLogo } from "@/components/brand/VatgerLogo"
import { Pill } from "@/components/efb/efb-ui"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Settings } from "lucide-react"
import type { ReactNode } from "react"

type EfbShellProps = {
  children: ReactNode
  headerStart?: ReactNode
  headerEnd?: ReactNode
  settingsOpen: boolean
  onSettingsToggle: () => void
}

export function EfbShell({
  children,
  headerStart,
  headerEnd,
  settingsOpen,
  onSettingsToggle,
}: EfbShellProps) {
  return (
    <div className="flex min-h-dvh w-full items-stretch justify-center p-0 min-[1400px]:min-h-screen min-[1400px]:items-center min-[1400px]:p-6">
      <div className="flex h-dvh w-full min-[1400px]:h-auto min-[1400px]:max-w-[1080px]">
        <div className="relative flex h-full w-full flex-col overflow-hidden border-0 bg-card min-[1400px]:aspect-[4/3] min-[1400px]:rounded-[1rem] min-[1400px]:border min-[1400px]:shadow-2xl">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(255,255,255,0.08),transparent_50%)] dark:bg-[radial-gradient(ellipse_at_top,rgba(255,255,255,0.06),transparent_55%)]" />

          <div className="relative flex min-h-0 flex-1 flex-col">
            <header className="flex shrink-0 items-center justify-between gap-3 border-b bg-background/60 px-4 py-3 backdrop-blur">
              <div className="flex min-w-0 items-center gap-3">
                <VatgerLogo />
                {!settingsOpen && headerStart}
              </div>

              <div className="flex shrink-0 items-center gap-2">
                {!settingsOpen && headerEnd}
                <Pill>{settingsOpen ? "Settings" : "EFB"}</Pill>
                <Button
                  type="button"
                  variant={settingsOpen ? "secondary" : "outline"}
                  size="icon-sm"
                  aria-label={settingsOpen ? "Close settings" : "Open settings"}
                  aria-pressed={settingsOpen}
                  onClick={onSettingsToggle}
                >
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </header>

            <main
              className={cn(
                "min-h-0 flex-1 overflow-y-auto p-4 min-[1400px]:overflow-hidden",
                settingsOpen && "bg-muted/10",
              )}
            >
              {children}
            </main>
          </div>
        </div>
      </div>
    </div>
  )
}
