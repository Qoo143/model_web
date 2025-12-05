import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import logger from '@/utils/logger'

interface User {
    id: number
    username: string
    email: string
    full_name?: string
    role: string
}

export const useAuthStore = defineStore('auth', () => {
    const token = ref<string | null>(localStorage.getItem('token'))
    const user = ref<User | null>(null)
    const isLoading = ref(false)

    const isLoggedIn = computed(() => !!token.value)

    const login = async (username: string, password: string) => {
        isLoading.value = true
        try {
            const formData = new FormData()
            formData.append('username', username)
            formData.append('password', password)

            const response = await api.post('/api/auth/login', formData)
            token.value = response.data.access_token
            localStorage.setItem('token', token.value!)

            logger.log('Login successful')
            await fetchUser()
            return { success: true }
        } catch (error: any) {
            logger.error('Login failed:', error)
            return {
                success: false,
                message: error.response?.data?.detail || '登入失敗'
            }
        } finally {
            isLoading.value = false
        }
    }

    const register = async (username: string, email: string, password: string) => {
        isLoading.value = true
        try {
            await api.post('/api/auth/register', { username, email, password })
            logger.log('Registration successful')
            return { success: true }
        } catch (error: any) {
            logger.error('Registration failed:', error)
            return {
                success: false,
                message: error.response?.data?.detail || '註冊失敗'
            }
        } finally {
            isLoading.value = false
        }
    }

    const fetchUser = async () => {
        if (!token.value) return
        try {
            const response = await api.get('/api/auth/me')
            user.value = response.data
            logger.log('User fetched:', user.value?.username)
        } catch (error) {
            logger.error('Failed to fetch user:', error)
            logout()
        }
    }

    const logout = () => {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
    }

    // 初始化時獲取用戶資訊
    if (token.value) {
        fetchUser()
    }

    return {
        token,
        user,
        isLoading,
        isLoggedIn,
        login,
        register,
        fetchUser,
        logout
    }
})
