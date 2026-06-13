import { CheckCircle2, XCircle } from "lucide-react"
import type { ReactNode } from "react"

export function Pill({
  children,
  variant = "default",
}: {
  children: ReactNode
  variant?: "default" | "success" | "warning" | "info"
}) {
  const base =
    "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium"
  const variants: Record<typeof variant, string> = {
    default: "bg-muted/40 text-foreground",
    success:
      "border-emerald-500/25 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
    warning:
      "border-amber-500/25 bg-amber-500/10 text-amber-800 dark:text-amber-300",
    info: "border-sky-500/25 bg-sky-500/10 text-sky-800 dark:text-sky-300",
  }

  return <span className={`${base} ${variants[variant]}`}>{children}</span>
}

export function SkeletonLine({ w = "w-full" }: { w?: string }) {
  return <div className={`h-3 ${w} animate-pulse rounded bg-muted`} />
}

export function FeedbackBanner({
  variant,
  message,
}: {
  variant: "success" | "error"
  message: string
}) {
  const isSuccess = variant === "success"
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
        isSuccess
          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-900 dark:text-emerald-100"
          : "border-destructive/30 bg-destructive/10 text-destructive"
      }`}
    >
      {isSuccess ? (
        <CheckCircle2 className="h-4 w-4 shrink-0" />
      ) : (
        <XCircle className="h-4 w-4 shrink-0" />
      )}
      <p>{message}</p>
    </div>
  )
}

export function PanelHeader({
  title,
  description,
  onClose,
  closeLabel = "Back to EFB",
}: {
  title: string
  description?: string
  onClose: () => void
  closeLabel?: string
}) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4 border-b pb-4">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
        {description ? (
          <p className="text-sm text-muted-foreground">{description}</p>
        ) : null}
      </div>
      <button
        type="button"
        onClick={onClose}
        className="shrink-0 text-sm font-medium text-primary underline-offset-4 hover:underline"
      >
        {closeLabel}
      </button>
    </div>
  )
}
