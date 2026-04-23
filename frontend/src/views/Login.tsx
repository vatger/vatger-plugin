import { selectUser, useAppSelector } from "@/app/auth"
import { useTheme } from "@/components/theme-provider"
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
	const user = useAppSelector(selectUser)
	const {theme} = useTheme()

	if(user) return (
		<div className="size-full flex justify-center items-center min-h-screen text-center">
				<Card>
					<img className="p-12 pb-4" src={theme === "dark" ? "/vatger_logo_light.svg" : "/vatger_logo_dark.svg"} />
					<h3 className="text-2xl font-semibold pb-6">Welcome to the vatger plugin!</h3>
				</Card>
		</div>
	)
	return (
		<div className="size-full flex justify-center items-center min-h-screen text-center">
				<Card>
					<img className="p-12 pb-4" src={theme === "dark" ? "/vatger_logo_light.svg" : "/vatger_logo_dark.svg"} />
					{error && (
						<p className="text-red-600 text-sm mb-3 max-w-50 text-center font-semibold">
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
