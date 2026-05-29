import { useResolvedTheme } from "@/components/theme-provider"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export const Login = ({
  onClick,
  loading = false,
  error,
}: {
  onClick: React.MouseEventHandler<HTMLButtonElement>
  loading?: boolean
  error?: string
}) => {
  const theme = useResolvedTheme()

  return (
    <div className="flex size-full min-h-screen items-center justify-center text-center">
      <Card>
        <img
          className="p-12 pb-4"
          src={
            theme === "dark"
              ? "/vatger_logo_light.svg"
              : "/vatger_logo_dark.svg"
          }
        />
        {error && (
          <p className="mb-3 max-w-50 text-center text-sm font-semibold text-red-600">
            {error}
          </p>
        )}
        <h3 className="text-2xl font-semibold">Sign in to the vatger plugin</h3>
        <Button className={"mx-6 my-2"} disabled={loading} onClick={onClick}>
          {loading ? "Logging in..." : "Login with VATSIM"}
        </Button>
      </Card>
    </div>
  )
}
