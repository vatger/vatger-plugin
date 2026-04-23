export const AuthCard = ({ children }: { children: React.JSX.Element }) => {
	return (
		<div
			className="flex flex-col justify-center items-center text-black p-10 border-2 border-[#232323] font-normal gap-2"
		>
			<div style={{ fontWeight: 500 }}></div>
			<img alt="Logo" draggable={false} src="/img/logo.webp" />
			<h1 className="text-3xl font-bold">vTFDPS</h1>
			<h3 className="max-w-50 text-center font-medium italic">
				Virtual Tower Flight Data Processing System
			</h3>

			{children}
		</div>
	)
}
