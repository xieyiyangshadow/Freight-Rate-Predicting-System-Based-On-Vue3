import apiClient from "./client"
import type { LoginRequest, RegisterRequest, AuthResponse } from "@/types/auth"

export const registerUser = async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register/', data)
    return response.data
}

export const loginUser = async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login/', data)
    return response.data
}

export const getCurrentUser = async (): Promise<void> => {
    const response = await apiClient.get('/auth/user/')
    return response.data
}

 export const logoutUser = async () => {
    return await apiClient.post('/auth/logout/')
}

export const refreshAccessToken = async (refreshToken: string) => {
    const response = await apiClient.post('/auth/refresh/', {
        refresh: refreshToken,
    })
    return response.data
}