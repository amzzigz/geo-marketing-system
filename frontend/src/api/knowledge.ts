import request from './index'

export interface KnowledgeItem {
  id: number
  file_name: string
  file_type: string
  file_size: number
  status: number
  created_at: string
  updated_at: string
}

export interface KnowledgeChunk {
  id: number
  chunk_order: number
  chunk_text: string
}

export interface KnowledgeDetail {
  id: number
  file_name: string
  file_type: string
  content_text: string
  chunks: KnowledgeChunk[]
}

export interface KnowledgeListResult {
  items: KnowledgeItem[]
  total: number
}

/** 上传企业资料文件 */
export function uploadKnowledgeApi(file: File): Promise<KnowledgeItem> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/api/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/** 获取企业资料列表 */
export function getKnowledgeListApi(page: number, page_size: number): Promise<KnowledgeListResult> {
  return request.get('/api/knowledge', { params: { page, page_size } })
}

/** 获取企业资料详情 */
export function getKnowledgeDetailApi(id: number): Promise<KnowledgeDetail> {
  return request.get(`/api/knowledge/${id}`)
}

/** 删除企业资料 */
export function deleteKnowledgeApi(id: number): Promise<void> {
  return request.delete(`/api/knowledge/${id}`)
}
