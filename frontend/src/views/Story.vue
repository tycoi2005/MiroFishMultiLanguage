<template>
  <div class="story-container">
    <!-- 顶部导航栏 -->
    <nav class="navbar navbar-dark">
      <div class="nav-brand">MIROFISH - STORY MODE (Testing)</div>
      <div class="nav-links">
        <router-link to="/" class="back-link">
          ← Back to Home
        </router-link>
        <LangSwitcher />
      </div>
    </nav>

    <div class="main-content">
      <!-- Hero 区域 -->
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">STORY TESTING</span>
            <span class="version-text">Beta Feature</span>
          </div>
          
          <h1 class="main-title">
            Story Mode<br>
            <span class="gradient-text">Testing Environment</span>
          </h1>
          
          <div class="hero-desc">
            <p>
              This is a hidden page for testing the <span class="highlight-bold">Story Mode</span> feature. 
              Generate narrative-style reports that transform prediction data into engaging stories.
            </p>
          </div>
        </div>
      </section>

      <!-- 主要内容 -->
      <section class="dashboard-section">
        <!-- 右栏：交互控制台 -->
        <div class="console-panel">
          <div class="console-box">
            <!-- Mode Display -->
            <div class="console-section">
              <div class="mode-display">
                <span class="mode-icon">📖</span>
                <span class="mode-label">{{ $t('home.modeStory') }}</span>
                <span class="mode-desc">{{ $t('home.modeStoryDesc') }}</span>
              </div>

              <!-- Story Format Selector -->
              <div class="format-selector">
                <button 
                  class="format-btn"
                  :class="{ active: formData.storyFormat === 'novel' }"
                  @click="formData.storyFormat = 'novel'"
                >
                  {{ $t('home.formatNovel') }}
                </button>
                <button 
                  class="format-btn"
                  :class="{ active: formData.storyFormat === 'screenplay' }"
                  @click="formData.storyFormat = 'screenplay'"
                >
                  {{ $t('home.formatScreenplay') }}
                </button>
              </div>
            </div>

            <!-- 上传区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ $t('home.console.seedLabel') }}</span>
                <span class="console-meta">{{ $t('home.console.seedFormats') }}</span>
              </div>
              
              <div 
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt"
                  @change="handleFileSelect"
                  style="display: none"
                  :disabled="loading"
                />
                
                <div v-if="files.length === 0" class="upload-placeholder">
                  <div class="upload-icon">↑</div>
                  <div class="upload-title">{{ $t('home.console.uploadTitle') }}</div>
                  <div class="upload-hint">{{ $t('home.console.uploadHint') }}</div>
                </div>
                
                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="console-divider">
              <span>{{ $t('home.console.inputParams') }}</span>
            </div>

            <!-- 输入区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">Story Prompt</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  :placeholder="$t('home.console.storyPromptPlaceholder')"
                  rows="6"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">STORY ENGINE</div>
              </div>
            </div>

            <!-- 启动按钮 -->
            <div class="console-section btn-section">
              <button 
                class="start-engine-btn"
                @click="startSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">{{ $t('home.console.startEngine') }}</span>
                <span v-else>{{ $t('home.console.initializing') }}</span>
                <span class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Note -->
      <div class="testing-note">
        <strong>Note:</strong> This page is for internal testing only. Story mode is still under development.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LangSwitcher from '../components/LangSwitcher.vue'

const { t } = useI18n()
const router = useRouter()

// 表单数据 - 默认为故事模式
const formData = ref({
  simulationRequirement: '',
  mode: 'story', // 固定为 story
  storyFormat: 'novel' // 默认小说格式
})

// 文件列表
const files = ref([])

// 状态
const loading = ref(false)
const isDragOver = ref(false)

// 文件输入引用
const fileInput = ref(null)

// 计算属性:是否可以提交
const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

// 触发文件选择
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

// 处理拖拽相关
const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return
  
  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

// 添加文件
const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

// 移除文件
const removeFile = (index) => {
  files.value.splice(index, 1)
}

// 开始模拟
const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  
  // Store mode in localStorage
  localStorage.setItem('mirofish-mode', formData.value.mode)
  
  // 存储待上传的数据
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement, formData.value.mode, formData.value.storyFormat)
    
    // 跳转到Process页面
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}
</script>

<style scoped>
/* Design tokens */
.story-container {
  --black: #000000;
  --white: #FFFFFF;
  --orange: #FF4500;
  --gray-light: #F5F5F5;
  --gray-text: #666666;
  --border: #E5E5E5;
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;

  min-height: 100vh;
  background: #FFFFFF;
  font-family: var(--font-sans);
  color: #000000;
}

/* Navbar */
.navbar {
  height: 60px;
  background: #000000;
  color: #FFFFFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.back-link {
  color: var(--white);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.back-link:hover {
  opacity: 1;
}

/* 主要内容区 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 40px;
}

/* Hero 区域 */
.hero-section {
  margin-bottom: 60px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.orange-tag {
  background: var(--orange);
  color: var(--white);
  padding: 4px 10px;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 0.75rem;
}

.version-text {
  color: #999;
  font-weight: 500;
}

.main-title {
  font-size: 3.5rem;
  line-height: 1.2;
  font-weight: 500;
  margin: 0 0 30px 0;
  letter-spacing: -2px;
}

.gradient-text {
  background: linear-gradient(90deg, #FF4500 0%, #FF6500 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--gray-text);
  max-width: 800px;
}

.highlight-bold {
  color: var(--black);
  font-weight: 700;
}

/* Dashboard */
.dashboard-section {
  display: flex;
  justify-content: center;
}

.console-panel {
  width: 100%;
  max-width: 600px;
}

.console-box {
  border: 1px solid #CCC;
  padding: 8px;
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
}

/* Mode Display */
.mode-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 20px;
  background: rgba(255, 69, 0, 0.05);
  border: 1px solid var(--orange);
  border-radius: 8px;
  margin-bottom: 16px;
}

.mode-icon {
  font-size: 32px;
}

.mode-label {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.mode-desc {
  font-size: 0.8rem;
  opacity: 0.7;
  text-align: center;
}

/* Format Selector */
.format-selector {
  display: flex;
  gap: 8px;
}

.format-btn {
  flex: 1;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--gray-text);
  font-family: var(--font-mono);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.format-btn:hover {
  border-color: #999;
}

.format-btn.active {
  border-color: var(--orange);
  background: rgba(255, 69, 0, 0.08);
  color: var(--black);
  font-weight: 600;
}

/* Console Header */
.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #666;
}

/* Upload Zone */
.upload-zone {
  border: 1px dashed #CCC;
  height: 200px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover {
  background: #F0F0F0;
  border-color: #999;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 40px;
  height: 40px;
  border: 1px solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: #999;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #999;
}

/* File List */
.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: var(--white);
  padding: 8px 12px;
  border: 1px solid #EEE;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
}

/* Console Divider */
.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #EEE;
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #BBB;
  letter-spacing: 1px;
}

/* Input Area */
.input-wrapper {
  position: relative;
  border: 1px solid #DDD;
  background: #FAFAFA;
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #AAA;
}

/* Start Button */
.start-engine-btn {
  width: 100%;
  background: var(--black);
  color: var(--white);
  border: none;
  padding: 20px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

.start-engine-btn:not(:disabled) {
  background: var(--black);
  border: 1px solid var(--black);
}

.start-engine-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
  transform: translateY(-2px);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #E5E5E5;
  color: #999;
  cursor: not-allowed;
  transform: none;
  border: 1px solid #E5E5E5;
}

/* Testing Note */
.testing-note {
  margin-top: 60px;
  padding: 20px;
  background: #FFF5E5;
  border: 1px solid #FFE0B3;
  border-radius: 4px;
  font-size: 0.9rem;
  text-align: center;
  color: #B87333;
}
</style>