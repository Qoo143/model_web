<template>
  <div class="documents-view">
    <!-- 頁面標題 -->
    <div class="page-header">
      <div class="header-left">
        <h2>文件管理</h2>
        <span v-if="chatStore.currentGroup" class="group-badge">
          {{ chatStore.currentGroup.name }}
        </span>
      </div>
      <button class="upload-btn" @click="showUploadModal = true" :disabled="!currentGroupId">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17,8 12,3 7,8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        上傳文件
      </button>
    </div>

    <!-- 無群組提示 -->
    <div v-if="!currentGroupId" class="no-group-hint">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
      <h3>請先選擇群組</h3>
      <p>在側邊欄選擇一個群組，或前往群組管理建立新群組</p>
      <router-link to="/groups" class="btn btn--primary">前往群組管理</router-link>
    </div>

    <!-- 文件列表 -->
    <div v-else class="documents-grid">
      <!-- 載入中 -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <span>載入中...</span>
      </div>

      <template v-else>
        <div 
          v-for="doc in documents" 
          :key="doc.id"
          class="document-card"
          :class="{ 'document-card--processing': doc.processing_status === 'processing' }"
        >
          <div class="doc-icon" :class="`doc-icon--${doc.processing_status}`">
            <!-- 處理中顯示 spinner -->
            <div v-if="doc.processing_status === 'processing'" class="spinner-small"></div>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14,2 14,8 20,8" />
              <line v-if="doc.processing_status === 'completed'" x1="9" y1="15" x2="15" y2="15" />
              <line v-if="doc.processing_status === 'completed'" x1="9" y1="11" x2="15" y2="11" />
            </svg>
          </div>
          <div class="doc-info">
            <div class="doc-name truncate">{{ doc.original_filename }}</div>
            <div class="doc-meta">
              <span>{{ formatFileSize(doc.file_size) }}</span>
              <span>•</span>
              <span :class="`status status--${doc.processing_status}`">
                {{ statusText(doc.processing_status) }}
              </span>
            </div>
            <!-- 處理中進度條 -->
            <div v-if="doc.processing_status === 'processing'" class="progress-bar">
              <div class="progress-bar-inner"></div>
            </div>
          </div>
          <button 
            class="doc-delete" 
            @click.stop="deleteDocument(doc.id)" 
            title="刪除"
            :disabled="isDeleting === doc.id"
          >
            <div v-if="isDeleting === doc.id" class="spinner-small"></div>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3,6 5,6 21,6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        </div>

        <!-- 空狀態 -->
        <div v-if="documents.length === 0" class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14,2 14,8 20,8" />
          </svg>
          <h3>尚無文件</h3>
          <p>上傳 txt 或 md 格式的文件開始使用</p>
        </div>
      </template>
    </div>

    <!-- 上傳彈窗 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal">
        <div class="modal-header">
          <h3>上傳文件</h3>
          <button class="modal-close" @click="closeUploadModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div 
            class="upload-zone"
            :class="{ 'upload-zone--dragover': isDragover }"
            @dragover.prevent="isDragover = true"
            @dragleave="isDragover = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".txt,.md"
              hidden
              @change="handleFileSelect"
            />
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17,8 12,3 7,8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p>拖放文件到此處，或點擊選擇</p>
            <span>支援 .txt, .md 格式</span>
          </div>

          <div v-if="selectedFile" class="selected-file">
            <span>{{ selectedFile.name }}</span>
            <button @click="selectedFile = null">✕</button>
          </div>

          <!-- 上傳進度 -->
          <div v-if="isUploading" class="upload-progress">
            <div class="progress-bar">
              <div class="progress-bar-inner" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <span>{{ uploadProgress }}%</span>
          </div>

          <div v-if="uploadError" class="upload-error">{{ uploadError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn--secondary" @click="closeUploadModal">取消</button>
          <button 
            class="btn btn--primary" 
            :disabled="!selectedFile || isUploading"
            @click="uploadFile"
          >
            {{ isUploading ? '上傳中...' : '上傳' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import api from '@/services/api'
import logger from '@/utils/logger'

interface Document {
  id: number
  original_filename: string
  file_size: number
  processing_status: string
}

const chatStore = useChatStore()
const documents = ref<Document[]>([])
const isLoading = ref(false)
const showUploadModal = ref(false)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadError = ref('')
const isDragover = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const isDeleting = ref<number | null>(null)

// 輪詢定時器
let pollingTimer: ReturnType<typeof setInterval> | null = null

// 使用 chat store 的 currentGroupId
const currentGroupId = computed(() => chatStore.currentGroupId)

const fetchDocuments = async () => {
  if (!currentGroupId.value) return
  isLoading.value = documents.value.length === 0  // 只在首次載入顯示 loading
  try {
    const response = await api.get('/api/documents', {
      params: { group_id: currentGroupId.value }
    })
    documents.value = response.data.documents || []
    logger.log('Documents loaded:', documents.value.length)
    
    // 檢查是否有處理中的文件，如果有則開始輪詢
    checkProcessingAndPoll()
  } catch (error) {
    logger.error('Failed to fetch documents:', error)
  } finally {
    isLoading.value = false
  }
}

// 檢查是否有處理中的文件並開始輪詢
const checkProcessingAndPoll = () => {
  const hasProcessing = documents.value.some(d => d.processing_status === 'processing' || d.processing_status === 'pending')
  
  if (hasProcessing && !pollingTimer) {
    // 開始輪詢，每 3 秒刷新一次
    pollingTimer = setInterval(() => {
      fetchDocuments()
    }, 3000)
    logger.log('Started polling for document status')
  } else if (!hasProcessing && pollingTimer) {
    // 停止輪詢
    clearInterval(pollingTimer)
    pollingTimer = null
    logger.log('Stopped polling - all documents processed')
  }
}

// 監聽群組變化
watch(currentGroupId, () => {
  if (currentGroupId.value) {
    fetchDocuments()
  } else {
    documents.value = []
  }
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.length) {
    selectedFile.value = input.files[0]
    uploadError.value = ''
  }
}

const handleDrop = (e: DragEvent) => {
  isDragover.value = false
  if (e.dataTransfer?.files.length) {
    const file = e.dataTransfer.files[0]
    if (file.name.endsWith('.txt') || file.name.endsWith('.md')) {
      selectedFile.value = file
      uploadError.value = ''
    } else {
      uploadError.value = '只支援 .txt 和 .md 格式'
    }
  }
}

const uploadFile = async () => {
  if (!selectedFile.value || !currentGroupId.value) return
  
  isUploading.value = true
  uploadProgress.value = 0
  uploadError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('group_id', currentGroupId.value.toString())
    
    await api.post('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      }
    })
    
    logger.log('File uploaded:', selectedFile.value.name)
    closeUploadModal()
    fetchDocuments()
  } catch (error: any) {
    uploadError.value = error.response?.data?.detail || '上傳失敗'
    logger.error('Upload failed:', error)
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFile.value = null
  uploadError.value = ''
  uploadProgress.value = 0
}

const deleteDocument = async (id: number) => {
  if (!confirm('確定要刪除此文件嗎？此操作無法復原。')) return
  
  isDeleting.value = id
  try {
    await api.delete(`/api/documents/${id}`)
    logger.log('Document deleted:', id)
    // 從列表中移除
    documents.value = documents.value.filter(d => d.id !== id)
  } catch (error: any) {
    logger.error('Failed to delete document:', error)
    alert(error.response?.data?.detail || '刪除失敗')
  } finally {
    isDeleting.value = null
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const statusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待處理',
    processing: '處理中...',
    completed: '已完成',
    failed: '處理失敗'
  }
  return map[status] || status
}

onMounted(() => {
  // 確保 groups 已載入
  if (chatStore.groups.length === 0) {
    chatStore.fetchGroups()
  }
  // 如果已有選中的群組，載入文件
  if (currentGroupId.value) {
    fetchDocuments()
  }
})

onUnmounted(() => {
  // 清理輪詢定時器
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
})
</script>

<style scoped>
.documents-view {
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

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.page-header h2 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
}

.group-badge {
  padding: 4px 12px;
  background-color: var(--color-accent-light);
  color: var(--color-accent);
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--radius-full);
}

.upload-btn {
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

.upload-btn:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-btn svg {
  width: 18px;
  height: 18px;
}

/* 無群組提示 */
.no-group-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  text-align: center;
  color: var(--color-text-tertiary);
}

.no-group-hint svg {
  width: 64px;
  height: 64px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.no-group-hint h3 {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.no-group-hint .btn {
  margin-top: var(--spacing-md);
}

/* 載入中 */
.loading-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
  color: var(--color-text-tertiary);
}

/* Spinner */
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 進度條 */
.progress-bar {
  height: 4px;
  background-color: var(--color-bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
  margin-top: var(--spacing-xs);
}

.progress-bar-inner {
  height: 100%;
  background-color: var(--color-accent);
  border-radius: 2px;
  transition: width 0.3s ease;
  animation: progressPulse 1.5s ease-in-out infinite;
}

@keyframes progressPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.upload-progress .progress-bar {
  flex: 1;
}

.upload-progress span {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  min-width: 40px;
  text-align: right;
}

/* 文件網格 */
.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
}

.document-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.document-card:hover {
  box-shadow: var(--shadow-md);
}

.document-card--processing {
  border-color: var(--color-accent);
  background-color: rgba(107, 154, 202, 0.05);
}

.doc-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-accent-light);
  border-radius: var(--radius-sm);
  color: var(--color-accent);
  flex-shrink: 0;
}

.doc-icon--completed {
  background-color: rgba(90, 196, 127, 0.15);
  color: var(--color-success);
}

.doc-icon--failed {
  background-color: rgba(199, 90, 90, 0.15);
  color: var(--color-error);
}

.doc-icon--processing {
  background-color: var(--color-accent-light);
}

.doc-icon svg {
  width: 22px;
  height: 22px;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.doc-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  display: flex;
  gap: var(--spacing-xs);
}

.status--completed { color: var(--color-success); }
.status--processing { color: var(--color-accent); }
.status--pending { color: var(--color-warning); }
.status--failed { color: var(--color-error); }

.doc-delete {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.doc-delete:hover:not(:disabled) {
  background-color: rgba(199, 90, 90, 0.1);
  color: var(--color-error);
}

.doc-delete:disabled {
  cursor: wait;
}

.doc-delete svg {
  width: 18px;
  height: 18px;
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

.upload-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.upload-zone:hover,
.upload-zone--dragover {
  border-color: var(--color-accent);
  background-color: var(--color-accent-light);
}

.upload-zone svg {
  width: 40px;
  height: 40px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-md);
}

.upload-zone p {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.upload-zone span {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
}

.selected-file button {
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  cursor: pointer;
}

.upload-error {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: rgba(199, 90, 90, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-sm);
  color: var(--color-error);
  font-size: var(--font-size-sm);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}

.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  text-decoration: none;
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
</style>
