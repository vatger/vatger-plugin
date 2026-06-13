import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react"

type EfbSettingsContextValue = {
  settingsOpen: boolean
  openSettings: () => void
  closeSettings: () => void
  toggleSettings: () => void
}

const EfbSettingsContext = createContext<EfbSettingsContextValue | undefined>(
  undefined,
)

export function EfbSettingsProvider({ children }: { children: ReactNode }) {
  const [settingsOpen, setSettingsOpen] = useState(false)

  const openSettings = useCallback(() => setSettingsOpen(true), [])
  const closeSettings = useCallback(() => setSettingsOpen(false), [])
  const toggleSettings = useCallback(
    () => setSettingsOpen((open) => !open),
    [],
  )

  const value = useMemo(
    () => ({
      settingsOpen,
      openSettings,
      closeSettings,
      toggleSettings,
    }),
    [settingsOpen, openSettings, closeSettings, toggleSettings],
  )

  return (
    <EfbSettingsContext.Provider value={value}>
      {children}
    </EfbSettingsContext.Provider>
  )
}

export function useEfbSettings() {
  const context = useContext(EfbSettingsContext)
  if (!context) {
    throw new Error("useEfbSettings must be used within EfbSettingsProvider")
  }
  return context
}
