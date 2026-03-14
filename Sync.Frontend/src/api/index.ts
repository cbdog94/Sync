import axios, { type AxiosResponse } from 'axios'

const instance = axios.create({
  baseURL: '/syncbackend',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应类型定义
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  result: T
}

export interface SubmitResult {
  code: string
}

export interface ExtractResult {
  text: string
}

export interface CheckFileResult {
  filename: string
}

// API 方法
export const api = {
  // 健康检查
  async health(): Promise<ApiResponse<null>> {
    const res: AxiosResponse<ApiResponse<null>> = await instance.get('/health')
    return res.data
  },

  // 提交文本
  async submit(text: string, once: boolean): Promise<ApiResponse<SubmitResult>> {
    const res: AxiosResponse<ApiResponse<SubmitResult>> = await instance.post('/submit', {
      text,
      once,
    })
    return res.data
  },

  // 提取文本
  async extract(code: string): Promise<ApiResponse<ExtractResult>> {
    const res: AxiosResponse<ApiResponse<ExtractResult>> = await instance.post('/extract', {
      code,
    })
    return res.data
  },

  // 上传文件
  async upload(file: File): Promise<ApiResponse<SubmitResult>> {
    const formData = new FormData()
    formData.append('file', file)
    const res: AxiosResponse<ApiResponse<SubmitResult>> = await instance.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return res.data
  },

  // 检查文件
  async checkFile(code: string): Promise<ApiResponse<CheckFileResult>> {
    const res: AxiosResponse<ApiResponse<CheckFileResult>> = await instance.get(`/checkfile/${code}`)
    return res.data
  },

  // 下载文件
  async download(code: string): Promise<Blob> {
    const res = await instance.get(`/download/${code}`, {
      responseType: 'blob',
    })
    return res.data
  },
}

export type Api = typeof api
