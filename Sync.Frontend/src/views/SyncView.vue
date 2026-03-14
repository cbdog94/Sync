<script setup lang="ts">
import { inject } from 'vue'
import { ElMessage } from 'element-plus'
import type { Api } from '@/api'

const api = inject<Api>('api')!

// 响应式状态
const loading = ref(false)
const text = ref('')
const once = ref(false)
const resultCode = ref('')
const showResult = ref(false)

// 提交同步
const handleSync = async () => {
  if (!text.value.trim()) {
    ElMessage.warning('请输入需要同步的文本！')
    return
  }

  loading.value = true
  try {
    const res = await api.submit(text.value, once.value)
    if (res.code !== 0) {
      ElMessage.error('同步失败!')
      return
    }
    resultCode.value = res.result.code
    showResult.value = true
    ElMessage.success('同步成功，请记录提取码！')
  } catch (error) {
    console.error(error)
    ElMessage.error('同步失败!')
  } finally {
    loading.value = false
  }
}

// 重置状态
const handleReset = () => {
  text.value = ''
  once.value = false
  resultCode.value = ''
  showResult.value = false
}

// 复制提取码
const { copy, isSupported } = useClipboard()

const handleCopy = async () => {
  if (isSupported) {
    await copy(resultCode.value)
    ElMessage.success('提取码已复制!')
  } else {
    ElMessage.warning('浏览器不支持自动复制')
  }
}
</script>

<template>
  <div class="sync-view" v-loading="loading">
    <h2>同步文本</h2>

    <template v-if="!showResult">
      <div class="input-container">
        <el-input
          v-model="text"
          type="textarea"
          :autosize="{ minRows: 4, maxRows: 12 }"
          placeholder="请输入需要同步的文本"
          class="text-input"
        />
        
        <el-checkbox v-model="once" class="once-checkbox">
          阅后即焚
        </el-checkbox>
      </div>

      <el-button
        type="primary"
        size="large"
        @click="handleSync"
        :disabled="loading"
      >
        同步
      </el-button>
    </template>

    <template v-else>
      <div class="result-container">
        <p class="result-label">提取码：</p>
        <p class="result-code" @click="handleCopy">{{ resultCode }}</p>
        <p class="result-hint">点击提取码可复制</p>
      </div>

      <div class="button-group">
        <el-button type="primary" size="large" @click="handleCopy">
          复制提取码
        </el-button>
        <el-button size="large" @click="handleReset">
          再次同步
        </el-button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.sync-view {
  max-width: 600px;
  margin: 0 auto;
}

.input-container {
  margin-bottom: 24px;
}

.text-input {
  width: 100%;
}

.once-checkbox {
  margin-top: 16px;
}

.result-container {
  margin-bottom: 24px;
}

.result-label {
  color: #606266;
  margin-bottom: 8px;
}

.result-code {
  font-size: 32px;
  font-weight: bold;
  color: #f56c6c;
  cursor: pointer;
  transition: transform 0.2s;
}

.result-code:hover {
  transform: scale(1.05);
}

.result-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.button-group {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
