import axios from 'axios'

// 開發環境使用 Vite proxy (/api -> localhost:8000)
// 生產環境可透過環境變數設定 API 位址
const api = axios.create({
    baseURL: '',  // 使用 Vite proxy
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 請求攔截器 - 添加 Token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// 響應攔截器 - 處理錯誤
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
