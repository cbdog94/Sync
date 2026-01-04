<script setup lang="ts">
// import { inject } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadProps, UploadProgressEvent, UploadFile, UploadRawFile } from 'element-plus'
import type { ApiResponse, SubmitResult } from '@/api'

// const api = inject<Api>('api')!

// 响应式状态
const resultCode = ref('')
const showResult = ref(false)
const uploadProgress = ref(0)
const showProgress = ref(false)

// 上传成功处理
const handleSuccess: UploadProps['onSuccess'] = (
  response: ApiResponse<SubmitResult>,
  _uploadFile: UploadFile
) => {
  showProgress.value = false
  uploadProgress.value = 0
  
  if (response.code !== 0) {
    ElMessage.error('上传失败!')
    console.error(response)
    return
  }
  
  resultCode.value = response.result.code
  showResult.value = true
  ElMessage.success('上传成功!')
}

// 上传失败处理
const handleError: UploadProps['onError'] = (error: Error) => {
  console.error(error)
  ElMessage.error('上传失败!')
  showProgress.value = false
  uploadProgress.value = 0
}

// 上传进度处理
const handleProgress: UploadProps['onProgress'] = (
  evt: UploadProgressEvent,
  _uploadFile: UploadFile
) => {
  showProgress.value = true
  uploadProgress.value = Math.floor(evt.percent ?? 0)
}

// 上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (_rawFile: UploadRawFile) => {
  return true
}

// 重置状态
const handleReset = () => {
  resultCode.value = ''
  showResult.value = false
  uploadProgress.value = 0
  showProgress.value = false
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
  <div class="upload-view">
    <h2>上传文件</h2>

    <template v-if="!showResult">
      <div class="upload-container">
        <el-upload
          drag
          action="/syncbackend/upload"
          :on-success="handleSuccess"
          :on-error="handleError"
          :on-progress="handleProgress"
          :before-upload="beforeUpload"
          :show-file-list="false"
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">
            将需要同步的文件拖到此处，或<em>点击上传</em>
          </div>
          
          <el-progress
            v-if="showProgress"
            :percentage="uploadProgress"
            :show-text="true"
            class="upload-progress"
          />
        </el-upload>
      </div>
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
          再次上传
        </el-button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.upload-view {
  max-width: 600px;
  margin: 0 auto;
}

.upload-container {
  margin-bottom: 24px;
}

.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-progress {
  width: 80%;
  margin: 16px auto 0;
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
