import { VatgerLogo } from "@/components/brand/VatgerLogo"
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
  return (
    <div className="flex size-full min-h-screen items-center justify-center text-center">
      <Card className="px-4">
        <VatgerLogo className="m-10 mb-4 h-16" />
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
