export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    username: string
    email: string
    password: string
    password2: string
}

export interface UserInfo {
    id: number
    username: string
    email: string
}

export interface AuthResponse {
    message: string
    user: UserInfo
    token: {
        refresh: string
        access: string
    }
}

export interface AuthState {
    user: UserInfo | null
    accessToken: string | null
    refreshToken: string | null
    isLoading: boolean
    error: string | null
}