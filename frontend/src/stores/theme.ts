import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
    // 從 localStorage 讀取或使用系統偏好
    const getInitialTheme = (): 'light' | 'dark' => {
        const saved = localStorage.getItem('theme')
        if (saved === 'light' || saved === 'dark') return saved

        // 檢查系統偏好
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark'
        }
        return 'light'
    }

    const theme = ref<'light' | 'dark'>(getInitialTheme())

    const toggleTheme = () => {
        theme.value = theme.value === 'light' ? 'dark' : 'light'
    }

    const setTheme = (newTheme: 'light' | 'dark') => {
        theme.value = newTheme
    }

    // 監聽變化並保存
    watch(theme, (newTheme) => {
        localStorage.setItem('theme', newTheme)
    })

    return {
        theme,
        toggleTheme,
        setTheme
    }
})
