<template>
  <div class="groups-view">
    <!-- 頁面標題 -->
    <div class="page-header">
      <h2>群組管理</h2>
      <button class="create-btn" @click="showCreateModal = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14" />
        </svg>
        建立群組
      </button>
    </div>

    <!-- 分類標籤 -->
    <div class="tabs">
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'my' }"
        @click="activeTab = 'my'"
      >
        我的群組
      </button>
      <button 
        class="tab" 
        :class="{ 'tab--active': activeTab === 'public' }"
        @click="activeTab = 'public'"
      >
        公開群組
      </button>
    </div>

    <!-- 群組列表 -->
    <div class="groups-grid">
      <div 
        v-for="group in filteredGroups" 
        :key="group.id"
        class="group-card"
        @click="openGroupDetail(group)"
      >
        <div class="group-icon" :class="{ 'group-icon--private': group.is_private }">
          <svg v-if="group.is_private" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        </div>
        <div class="group-info">
          <div class="group-name">{{ group.name }}</div>
          <div class="group-meta">
            <span>{{ group.member_count }} 位成員</span>
            <span>•</span>
            <span>{{ group.document_count }} 份文件</span>
          </div>
          <div v-if="group.description" class="group-desc truncate">
            {{ group.description }}
          </div>
        </div>
        <div class="group-badge" v-if="group.owner_id === userId">
          管理員
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-if="filteredGroups.length === 0 && !isLoading" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
        <h3 v-if="activeTab === 'my'">尚無群組</h3>
        <h3 v-else>尚無公開群組</h3>
        <p v-if="activeTab === 'my'">點擊「建立群組」開始</p>
      </div>
    </div>

    <!-- 建立群組彈窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal">
        <div class="modal-header">
          <h3>建立群組</h3>
          <button class="modal-close" @click="closeCreateModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
        <form @submit.prevent="createGroup" class="modal-body">
          <div class="form-group">
            <label>群組名稱 *</label>
            <input 
              v-model="createForm.name"
              type="text"
              placeholder="輸入群組名稱"
              required
            />
          </div>

          <div class="form-group">
            <label>描述</label>
            <textarea 
              v-model="createForm.description"
              placeholder="群組描述（選填）"
              rows="3"
            />
          </div>

          <div class="form-group">
            <label>群組類型</label>
            <div class="radio-group">
              <label class="radio-item">
                <input 
                  type="radio" 
                  v-model="createForm.is_private" 
                  :value="true"
                />
                <span class="radio-label">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  私人群組
                </span>
                <span class="radio-desc">只有受邀成員可以加入</span>
              </label>
              <label class="radio-item">
                <input 
                  type="radio" 
                  v-model="createForm.is_private" 
                  :value="false"
                />
                <span class="radio-label">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="2" y1="12" x2="22" y2="12" />
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                  </svg>
                  公開群組
                </span>
                <span class="radio-desc">所有人可見並申請加入</span>
              </label>
            </div>
          </div>

          <div v-if="createError" class="error-message">{{ createError }}</div>
        </form>
        <div class="modal-footer">
          <button class="btn btn--secondary" @click="closeCreateModal">取消</button>
          <button 
            class="btn btn--primary" 
            :disabled="!createForm.name || isCreating"
            @click="createGroup"
          >
            {{ isCreating ? '建立中...' : '建立' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 群組詳情彈窗 -->
    <div v-if="selectedGroup" class="modal-overlay" @click.self="selectedGroup = null">
      <div class="modal modal--large">
        <div class="modal-header">
          <h3>{{ selectedGroup.name }}</h3>
          <button class="modal-close" @click="selectedGroup = null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <div class="detail-row">
              <span class="detail-label">狀態</span>
              <span class="detail-value">
                <span class="badge" :class="selectedGroup.is_private ? 'badge--private' : 'badge--public'">
                  {{ selectedGroup.is_private ? '私人' : '公開' }}
                </span>
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">成員</span>
              <span class="detail-value">{{ selectedGroup.member_count }} 人</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">文件</span>
              <span class="detail-value">{{ selectedGroup.document_count }} 份</span>
            </div>
            <div v-if="selectedGroup.description" class="detail-row">
              <span class="detail-label">描述</span>
              <span class="detail-value">{{ selectedGroup.description }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button 
            v-if="selectedGroup.owner_id === userId"
            class="btn btn--danger" 
            @click="deleteGroup(selectedGroup.id)"
          >
            刪除群組
          </button>
          <button class="btn btn--primary" @click="enterGroup(selectedGroup)">
            進入群組
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import api from '@/services/api'
import logger from '@/utils/logger'

interface Group {
  id: number
  name: string
  description?: string
  is_private: boolean
  owner_id: number
  member_count: number
  document_count: number
}

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const userId = computed(() => authStore.user?.id)
const groups = ref<Group[]>([])
const isLoading = ref(false)
const activeTab = ref<'my' | 'public'>('my')

const filteredGroups = computed(() => {
  if (activeTab.value === 'my') {
    return groups.value
  }
  return groups.value.filter(g => !g.is_private)
})

// 建立群組
const showCreateModal = ref(false)
const isCreating = ref(false)
const createError = ref('')
const createForm = reactive({
  name: '',
  description: '',
  is_private: true
})

// 群組詳情
const selectedGroup = ref<Group | null>(null)

const fetchGroups = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/api/groups')
    groups.value = response.data.groups || []
    logger.log('Groups loaded:', groups.value.length)
  } catch (error) {
    logger.error('Failed to fetch groups:', error)
  } finally {
    isLoading.value = false
  }
}

const createGroup = async () => {
  if (!createForm.name) return
  
  isCreating.value = true
  createError.value = ''
  
  try {
    await api.post('/api/groups', {
      name: createForm.name,
      description: createForm.description || undefined,
      is_private: createForm.is_private
    })
    
    logger.log('Group created:', createForm.name)
    closeCreateModal()
    fetchGroups()
    chatStore.fetchGroups()
  } catch (error: any) {
    createError.value = error.response?.data?.detail || '建立失敗'
    logger.error('Failed to create group:', error)
  } finally {
    isCreating.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  createForm.name = ''
  createForm.description = ''
  createForm.is_private = true
  createError.value = ''
}

const openGroupDetail = (group: Group) => {
  selectedGroup.value = group
}

const enterGroup = (group: Group) => {
  chatStore.selectGroup(group.id)
  selectedGroup.value = null
  router.push('/')
}

const deleteGroup = async (groupId: number) => {
  if (!confirm('確定要刪除此群組嗎？此操作無法復原。')) return
  
  try {
    await api.delete(`/api/groups/${groupId}`)
    logger.log('Group deleted:', groupId)
    selectedGroup.value = null
    fetchGroups()
    chatStore.fetchGroups()
  } catch (error) {
    logger.error('Failed to delete group:', error)
  }
}

onMounted(() => {
  fetchGroups()
})
</script>

<style scoped>
.groups-view {
  padding: var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}

.page-header h2 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
}

.create-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background-color: var(--color-accent);
  color: white;
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}

.create-btn:hover {
  background-color: var(--color-accent-hover);
}

.create-btn svg {
  width: 18px;
  height: 18px;
}

/* 分類標籤 */
.tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: var(--spacing-sm);
}

.tab {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.tab:hover {
  color: var(--color-text-primary);
  background-color: var(--color-bg-tertiary);
}

.tab--active {
  color: var(--color-accent);
  background-color: var(--color-accent-light);
}

/* 群組網格 */
.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-md);
}

.group-card {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.group-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-accent);
}

.group-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-accent-light);
  border-radius: var(--radius-md);
  color: var(--color-accent);
  flex-shrink: 0;
}

.group-icon--private {
  background-color: rgba(196, 163, 90, 0.15);
  color: var(--color-warning);
}

.group-icon svg {
  width: 24px;
  height: 24px;
}

.group-info {
  flex: 1;
  min-width: 0;
}

.group-name {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.group-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  display: flex;
  gap: var(--spacing-xs);
}

.group-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.group-badge {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  padding: 2px 8px;
  background-color: var(--color-accent);
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: var(--radius-full);
}

/* 空狀態 */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-tertiary);
  text-align: center;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

/* 彈窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: var(--spacing-lg);
}

.modal {
  width: 100%;
  max-width: 480px;
  background-color: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.modal--large {
  max-width: 560px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.modal-header h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  border-radius: var(--radius-sm);
}

.modal-close:hover {
  background-color: var(--color-bg-tertiary);
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: var(--spacing-lg);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}

/* 表單 */
.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-family: inherit;
  transition: border-color var(--transition-fast);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-accent);
}

.form-group textarea {
  resize: vertical;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.radio-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.radio-item:has(input:checked) {
  border-color: var(--color-accent);
  background-color: var(--color-accent-light);
}

.radio-item input {
  width: auto;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-weight: 500;
  color: var(--color-text-primary);
}

.radio-label svg {
  width: 18px;
  height: 18px;
}

.radio-desc {
  width: 100%;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-left: 24px;
}

.error-message {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: rgba(199, 90, 90, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-sm);
  color: var(--color-error);
  font-size: var(--font-size-sm);
}

/* 詳情 */
.detail-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.detail-value {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.badge {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  border-radius: var(--radius-full);
}

.badge--private {
  background-color: rgba(196, 163, 90, 0.15);
  color: var(--color-warning);
}

.badge--public {
  background-color: var(--color-accent-light);
  color: var(--color-accent);
}

/* 按鈕 */
.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.btn--secondary {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.btn--secondary:hover {
  background-color: var(--color-border);
}

.btn--primary {
  background-color: var(--color-accent);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
}

.btn--primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--danger {
  background-color: var(--color-error);
  color: white;
}

.btn--danger:hover {
  opacity: 0.9;
}
</style>
