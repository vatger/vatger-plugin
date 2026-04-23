import {
	type BaseQueryFn,
	type FetchArgs,
	type FetchBaseQueryError,
	fetchBaseQuery,
} from "@reduxjs/toolkit/query"
import { AuthError, refreshTokens } from "./api"
import { clearUser } from "./slice"

export const baseQuery = fetchBaseQuery({
	baseUrl: "/api/",
	credentials: "include",
	responseHandler: async (response) => {
		const text = await response.text()
		return text.length ? JSON.parse(text) : null
	},
})

let inflightRefresh: Promise<void> | null = null

export const baseQueryWithAuth: BaseQueryFn<
	string | FetchArgs,
	unknown,
	FetchBaseQueryError
> = async (args, api, extraOptions) => {
	let result = await baseQuery(args, api, extraOptions)

	if (result.error?.status !== 401) return result

	try {
		inflightRefresh ??= refreshTokens().finally(() => {
			inflightRefresh = null
		})
		await inflightRefresh

		result = await baseQuery(args, api, extraOptions)
	} catch (e) {
		if (e instanceof AuthError && e.code === "refresh_failed") {
			api.dispatch(clearUser())
			window.location.replace("/auth")
		}
	}

	return result
}
