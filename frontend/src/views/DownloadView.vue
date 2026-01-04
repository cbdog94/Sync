<script setup lang="ts">
import { inject } from 'vue'
import { ElMessage } from 'element-plus'
import type { Api } from '@/api'

const api = inject<Api>('api')!

// 响应式状态
const loading = ref(false)
const code = ref('')
const showResult = ref(false)

// 下载文件
const handleDownload = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入提取码！')
    return
  }

  loading.value = true
  try {
    // 先检查文件是否存在
    const checkRes = await api.checkFile(code.value)
    
    if (checkRes.code === 1) {
      ElMessage.error('提取失败!')
      return
    }
    
    if (checkRes.code === 2) {
      ElMessage.warning('文件不存在')
      return
    }

    // 下载文件
    const blob = await api.download(code.value)
    const filename = checkRes.result.filename
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    showResult.value = true
    ElMessage.success('提取成功!')
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
  showResult.value = false
}
</script>

<template>
  <div class="download-view" v-loading="loading">
    <h2>提取文件</h2>

    <template v-if="!showResult">
      <div class="input-container">
        <el-form @submit.prevent="handleDownload">
          <el-form-item label="提取码">
            <el-input
              v-model="code"
              placeholder="请输入4位提取码"
              maxlength="4"
              @keyup.enter="handleDownload"
              class="code-input"
            />
          </el-form-item>
        </el-form>
      </div>

      <el-button
        type="primary"
        size="large"
        @click="handleDownload"
        :disabled="loading"
      >
        提取
      </el-button>
    </template>

    <template v-else>
      <div class="result-container">
        <el-icon class="success-icon"><CircleCheckFilled /></el-icon>
        <p class="success-text">文件下载成功！</p>
      </div>

      <el-button size="large" @click="handleReset">
        再次提取
      </el-button>
    </template>
  </div>
</template>

<style scoped>
.download-view {
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

.success-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 16px;
}

.success-text {
  font-size: 18px;
  color: #303133;
}
</style>
