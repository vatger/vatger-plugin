import { useTheme, type Theme } from "@/components/theme-provider"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Toggle } from "@/components/ui/toggle"
import { Monitor, Moon, Sun } from "lucide-react"

const THEME_OPTIONS: {
  value: Theme
  label: string
  icon: typeof Sun
}[] = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
]

export function ThemeSelector() {
  const { theme, setTheme } = useTheme()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Appearance</CardTitle>
        <CardDescription>Choose how the EFB is displayed</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-2">
        {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
          <Toggle
            key={value}
            pressed={theme === value}
            onPressedChange={() => setTheme(value)}
            size="lg"
            variant="outline"
            aria-label={`${label} theme`}
          >
            <Icon />
            {label}
          </Toggle>
        ))}
      </CardContent>
    </Card>
  )
}
