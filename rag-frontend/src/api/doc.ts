import request from '@/utils/request'

export interface UploadResponse {
  status: string
  doc_id: string
  length: number
  message?: string
}

export function uploadDocument(formData: FormData) {
  return request<any, UploadResponse>({
    url: '/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export interface DocItem {
  id: string
  name: string
  upload_time: string
  status: string
  size?: number
}

export function getDocList() {
  return request<any, DocItem[]>({
    url: '/docs/list',
    method: 'get',
  })
}
