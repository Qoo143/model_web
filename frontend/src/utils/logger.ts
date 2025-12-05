/**
 * Logger - 開發模式日誌工具
 * 只在開發環境輸出日誌，生產環境不顯示
 */

const isDev = import.meta.env.DEV

export const logger = {
    log: (...args: any[]) => {
        if (isDev) console.log('[DEV]', ...args)
    },

    info: (...args: any[]) => {
        if (isDev) console.info('[INFO]', ...args)
    },

    warn: (...args: any[]) => {
        if (isDev) console.warn('[WARN]', ...args)
    },

    error: (...args: any[]) => {
        // 錯誤訊息在生產環境也輸出
        console.error('[ERROR]', ...args)
    },

    debug: (...args: any[]) => {
        if (isDev) console.debug('[DEBUG]', ...args)
    },

    group: (label: string) => {
        if (isDev) console.group(label)
    },

    groupEnd: () => {
        if (isDev) console.groupEnd()
    }
}

export default logger
