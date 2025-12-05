import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import logger from '@/utils/logger'

interface Group {
    id: number
    name: string
    description?: string
    member_count: number
    document_count: number
}

interface Conversation {
    id: number
    title: string
    group_id: number
    message_count: number
    created_at: string
    updated_at: string
}

interface Source {
    document_id: number
    document_name: string
    content: string
    score: number
}

interface Message {
    id: number
    role: 'user' | 'assistant'
    content: string
    sources?: Source[]
    created_at: string
}

export const useChatStore = defineStore('chat', () => {
    // 群組
    const groups = ref<Group[]>([])
    const currentGroupId = ref<number | null>(null)
    const currentGroup = computed(() =>
        groups.value.find(g => g.id === currentGroupId.value) || null
    )

    // 對話
    const conversations = ref<Conversation[]>([])
    const currentConversationId = ref<number | null>(null)
    const currentConversation = computed(() =>
        conversations.value.find(c => c.id === currentConversationId.value) || null
    )

    // 訊息
    const messages = ref<Message[]>([])
    const isLoading = ref(false)
    const isSending = ref(false)

    // 載入群組
    const fetchGroups = async () => {
        try {
            const response = await api.get('/api/groups')
            groups.value = response.data.groups || []
            logger.log('Groups loaded:', groups.value.length)

            // 自動選擇第一個群組
            if (groups.value.length > 0 && !currentGroupId.value) {
                selectGroup(groups.value[0].id)
            }
        } catch (error) {
            logger.error('Failed to fetch groups:', error)
        }
    }

    // 選擇群組
    const selectGroup = async (groupId: number) => {
        currentGroupId.value = groupId
        currentConversationId.value = null
        messages.value = []
        logger.log('Group selected:', groupId)
        await fetchConversations()
    }

    // 載入對話列表
    const fetchConversations = async () => {
        if (!currentGroupId.value) return

        try {
            const response = await api.get('/api/chat/conversations', {
                params: { group_id: currentGroupId.value }
            })
            conversations.value = response.data.conversations || []
            logger.log('Conversations loaded:', conversations.value.length)
        } catch (error) {
            logger.error('Failed to fetch conversations:', error)
        }
    }

    // 選擇對話
    const selectConversation = async (conversationId: number) => {
        currentConversationId.value = conversationId
        await fetchMessages()
    }

    // 載入訊息
    const fetchMessages = async () => {
        if (!currentConversationId.value) return

        isLoading.value = true
        try {
            const response = await api.get(`/api/chat/conversations/${currentConversationId.value}`)
            messages.value = response.data.messages || []
            logger.log('Messages loaded:', messages.value.length)
        } catch (error) {
            logger.error('Failed to fetch messages:', error)
        } finally {
            isLoading.value = false
        }
    }

    // 發送訊息
    const sendMessage = async (question: string): Promise<boolean> => {
        if (!currentGroupId.value || isSending.value) return false

        isSending.value = true
        logger.log('Sending message:', question.substring(0, 50))

        // 添加用戶訊息到列表
        const userMessage: Message = {
            id: Date.now(),
            role: 'user',
            content: question,
            created_at: new Date().toISOString()
        }
        messages.value.push(userMessage)

        try {
            const response = await api.post('/api/chat/ask', {
                question,
                group_id: currentGroupId.value,
                conversation_id: currentConversationId.value
            })

            const data = response.data
            currentConversationId.value = data.conversation_id

            // 添加助手回覆
            const assistantMessage: Message = {
                id: data.message_id,
                role: 'assistant',
                content: data.answer,
                sources: data.sources,
                created_at: new Date().toISOString()
            }
            messages.value.push(assistantMessage)

            logger.log('Message sent successfully')

            // 刷新對話列表
            await fetchConversations()

            return true
        } catch (error: any) {
            logger.error('Failed to send message:', error)

            // 添加錯誤訊息
            messages.value.push({
                id: Date.now(),
                role: 'assistant',
                content: error.response?.data?.detail || '抱歉，處理您的問題時發生錯誤。請稍後再試。',
                created_at: new Date().toISOString()
            })

            return false
        } finally {
            isSending.value = false
        }
    }

    // 建立新對話
    const createNewConversation = () => {
        currentConversationId.value = null
        messages.value = []
        logger.log('New conversation created')
    }

    // 刪除對話
    const deleteConversation = async (conversationId: number) => {
        try {
            await api.delete(`/api/chat/conversations/${conversationId}`)

            if (currentConversationId.value === conversationId) {
                currentConversationId.value = null
                messages.value = []
            }

            await fetchConversations()
            logger.log('Conversation deleted:', conversationId)
        } catch (error) {
            logger.error('Failed to delete conversation:', error)
        }
    }

    return {
        // 群組
        groups,
        currentGroupId,
        currentGroup,
        fetchGroups,
        selectGroup,

        // 對話
        conversations,
        currentConversationId,
        currentConversation,
        fetchConversations,
        selectConversation,
        createNewConversation,
        deleteConversation,

        // 訊息
        messages,
        isLoading,
        isSending,
        fetchMessages,
        sendMessage
    }
})
