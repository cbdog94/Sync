<script setup lang="ts">
import { inject } from 'vue'
import { ElMessage } from 'element-plus'
import type { Api } from '@/api'

const api = inject<Api>('api')!

// 响应式状态
const loading = ref(false)
const code = ref('')
const extractedText = ref('')
const showResult = ref(false)

// 提取文本
const handleExtract = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入提取码！')
    return
  }

  loading.value = true
  try {
    const res = await api.extract(code.value)
    
    if (res.code === 1) {
      ElMessage.error('提取失败!')
      return
    }
    
    if (res.code === 2) {
      ElMessage.warning('提取文本不存在')
      return
    }

    extractedText.value = res.result.text
    showResult.value = true
    
    // 尝试自动复制到剪贴板（Safari 等浏览器可能会因安全限制失败）
    if (isSupported.value) {
      try {
        await navigator.clipboard.writeText(res.result.text)
        ElMessage.success('提取成功，已自动复制!')
      } catch {
        // Safari 在非用户交互上下文中会失败
        ElMessage.success('提取成功！点击下方按钮复制')
      }
    } else {
      ElMessage.success('提取成功!')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('提取失败!')
  } finally {
    loading.value = false
  }
}

// 重置状态
const handleReset = () => {
  code.value = ''
  extractedText.value = ''
  showResult.value = false
}

// 复制文本
const { copy, isSupported } = useClipboard()

const handleCopy = async (showMessage = true) => {
  if (isSupported) {
    await copy(extractedText.value)
    if (showMessage) {
      ElMessage.success('文本已复制!')
    }
  } else {
    ElMessage.warning('浏览器不支持自动复制')
  }
}
</script>

<template>
  <div class="extract-view" v-loading="loading">
    <h2>提取文本</h2>

    <template v-if="!showResult">
      <div class="input-container">
        <el-form @submit.prevent="handleExtract">
          <el-form-item label="提取码">
            <el-input
              v-model="code"
              placeholder="请输入4位提取码"
              maxlength="4"
              @keyup.enter="handleExtract"
              class="code-input"
            />
          </el-form-item>
        </el-form>
      </div>

      <el-button
        type="primary"
        size="large"
        @click="handleExtract"
        :disabled="loading"
      >
        提取
      </el-button>
    </template>

    <template v-else>
      <div class="result-container">
        <div class="text-display">
          {{ extractedText }}
        </div>
      </div>

      <div class="button-group">
        <el-button type="primary" size="large" @click="() => handleCopy()">
          复制文本
        </el-button>
        <el-button size="large" @click="handleReset">
          再次提取
        </el-button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.extract-view {
  max-width: 600px;
  margin: 0 auto;
}

.input-container {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.code-input {
  width: 120px;
}

.result-container {
  margin-bottom: 24px;
}

.text-display {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
  text-align: left;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
  color: #303133;
  line-height: 1.6;
}

.button-group {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
