import request from './index'

export interface PromptItem {
  id: number
  user_id: number | null
  name: string
  prompt_type: 'title' | 'content' | 'fusion'
  content_type: string | null
  platform: string | null
  prompt_text: string
  is_default: boolean
  status: number
  created_at: string
  updated_at: string
}

export interface PromptListResult {
  items: PromptItem[]
  total: number
  page: number
  page_size: number
}

export interface PromptListParams {
  page?: number
  page_size?: number
  prompt_type?: string
  platform?: string
  name?: string
  start_date?: string
  end_date?: string
}

export interface PromptCreateData {
  name: string
  prompt_type: 'title' | 'content' | 'fusion'
  content_type?: string
  platform?: string
  prompt_text: string
}

export interface PromptUpdateData {
  name?: string
  prompt_type?: 'title' | 'content' | 'fusion'
  content_type?: string
  platform?: string
  prompt_text?: string
}

/** 获取指令列表 */
export function getPromptsApi(params: PromptListParams): Promise<PromptListResult> {
  return request.get('/api/prompts', { params })
}

/** 获取指令详情 */
export function getPromptDetailApi(id: number): Promise<PromptItem> {
  return request.get(`/api/prompts/${id}`)
}

/** 创建指令 */
export function createPromptApi(data: PromptCreateData): Promise<PromptItem> {
  return request.post('/api/prompts', data)
}

/** 更新指令 */
export function updatePromptApi(id: number, data: PromptUpdateData): Promise<PromptItem> {
  return request.put(`/api/prompts/${id}`, data)
}

/** 删除指令 */
export function deletePromptApi(id: number): Promise<void> {
  return request.delete(`/api/prompts/${id}`)
}

/** 批量删除指令 */
export function batchDeletePromptsApi(ids: number[]): Promise<{ deleted_count: number }> {
  return request.delete('/api/prompts/batch', { data: { ids } })
}
