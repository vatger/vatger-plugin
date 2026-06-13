import { PanelHeader } from "@/components/efb/efb-ui"
import { PluginTokenList } from "@/components/settings/PluginTokenList"
import { ThemeSelector } from "@/components/settings/ThemeSelector"

type SettingsPanelProps = {
  onClose: () => void
}

export function SettingsPanel({ onClose }: SettingsPanelProps) {
  return (
    <div className="mx-auto w-full max-w-lg">
      <PanelHeader
        title="Settings"
        description="Appearance and plugin access for this account"
        onClose={onClose}
      />
      <div className="flex flex-col gap-4">
        <ThemeSelector />
        <PluginTokenList />
      </div>
    </div>
  )
}
