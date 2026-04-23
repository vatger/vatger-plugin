import { createSlice, type PayloadAction } from "@reduxjs/toolkit"
import type { RootState } from "./store"

export interface User {
	cid: string
	admin: boolean
	access: boolean
}

interface AuthState {
	user: User | null
}

const initialState: AuthState = { user: null }

const authSlice = createSlice({
	name: "auth",
	initialState,
	reducers: {
		setUser(state, action: PayloadAction<User>) {
			state.user = action.payload
		},
		clearUser(state) {
			state.user = null
		},
	},
})

export const selectUser = (state: RootState) => state.auth.user
export const { setUser, clearUser } = authSlice.actions
export const { reducer: authReducer } = authSlice
