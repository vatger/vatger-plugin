import { fetchPilotConnection } from "@/app/datafeed"
import { useEfbSettings } from "@/app/efb"
import {
  createSilentRequest,
  deleteSilentRequest,
  fetchSilentRequest,
  type RequestType,
} from "@/app/silent-request"
import {
  CallsignPill,
  ConnectionStatusPills,
} from "@/components/efb/ConnectionHeader"
import { EfbShell } from "@/components/efb/EfbShell"
import { DashboardGrid } from "@/components/dashboard/DashboardGrid"
import { SettingsPanel } from "@/components/settings/SettingsPanel"
import { useZuluClock } from "@/hooks/useZuluClock"
import { formatRequestType } from "@/lib/format"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"

const SILENT_REQUEST_KEY = ["silentRequest"] as const
const CONNECTION_KEY = ["connectionData"] as const

const FEEDBACK_AUTO_DISMISS_MS = {
  success: 3500,
  error: 5500,
} as const

export const Efb = () => {
  const queryClient = useQueryClient()
  const { settingsOpen, closeSettings, toggleSettings } = useEfbSettings()
  const zuluTime = useZuluClock()
  const [selectedType, setSelectedType] = useState<RequestType>()
  const [feedback, setFeedback] = useState<{
    variant: "success" | "error"
    message: string
  } | null>(null)

  const {
    data: connectionData,
    isError: connectionError,
    isPending: connectionPending,
  } = useQuery({
    queryKey: CONNECTION_KEY,
    queryFn: fetchPilotConnection,
    refetchInterval: 10_000,
    enabled: !settingsOpen,
  })

  const {
    data: pendingRequest,
    isPending: pendingLoading,
    isFetching: pendingFetching,
  } = useQuery({
    queryKey: SILENT_REQUEST_KEY,
    queryFn: fetchSilentRequest,
    refetchInterval: 5_000,
    enabled: !settingsOpen,
  })

  useEffect(() => {
    if (pendingRequest) {
      setSelectedType(pendingRequest.type)
    }
  }, [pendingRequest])

  useEffect(() => {
    if (!feedback) return
    const timeout = window.setTimeout(
      () => setFeedback(null),
      FEEDBACK_AUTO_DISMISS_MS[feedback.variant],
    )
    return () => window.clearTimeout(timeout)
  }, [feedback])

  const sendRequest = useMutation({
    mutationFn: createSilentRequest,
    onSuccess: (_data, type) => {
      void queryClient.invalidateQueries({ queryKey: SILENT_REQUEST_KEY })
      setFeedback({
        variant: "success",
        message: `${formatRequestType(type)} request sent to ATC.`,
      })
    },
    onError: (error: Error) => {
      setFeedback({ variant: "error", message: error.message })
    },
  })

  const cancelRequest = useMutation({
    mutationFn: deleteSilentRequest,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: SILENT_REQUEST_KEY })
      setSelectedType(undefined)
      setFeedback({
        variant: "success",
        message: "Pending request cancelled.",
      })
    },
    onError: (error: Error) => {
      setFeedback({ variant: "error", message: error.message })
    },
  })

  const isOnline = !!connectionData
  const callsign = connectionData?.callsign ?? "—"
  const hasPending = !!pendingRequest
  const pendingSameType =
    hasPending && selectedType && pendingRequest.type === selectedType
  const canSendRequest =
    isOnline && selectedType && !sendRequest.isPending && !pendingSameType

  return (
    <EfbShell
      settingsOpen={settingsOpen}
      onSettingsToggle={toggleSettings}
      headerStart={
        <ConnectionStatusPills
          isOnline={isOnline}
          connectionPending={connectionPending}
          zuluTime={zuluTime}
        />
      }
      headerEnd={<CallsignPill callsign={callsign} />}
    >
      {settingsOpen ? (
        <SettingsPanel onClose={closeSettings} />
      ) : (
        <DashboardGrid
          connection={connectionData}
          connectionPending={connectionPending}
          connectionError={connectionError}
          isOnline={isOnline}
          selectedType={selectedType}
          onSelectType={setSelectedType}
          pendingRequest={pendingRequest}
          pendingLoading={pendingLoading}
          pendingFetching={pendingFetching}
          feedback={feedback}
          canSendRequest={!!canSendRequest}
          sendPending={sendRequest.isPending}
          cancelPending={cancelRequest.isPending}
          pendingSameType={!!pendingSameType}
          onSend={() => {
            if (!selectedType) return
            setFeedback(null)
            sendRequest.mutate(selectedType)
          }}
          onCancel={() => cancelRequest.mutate()}
        />
      )}
    </EfbShell>
  )
}
