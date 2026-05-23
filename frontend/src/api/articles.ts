import request from './index'

export interface ArticleItem {
  id: number
  title: string
  keyword: string
  status: 'review' | 'published' | 'rejected'
  created_at: string
  updated_at: string
}

export interface ArticleListResult {
  items: ArticleItem[]
  total: number
  page: number
  page_size: number
}

export interface ArticleGenerateData {
  keyword_id: number
  expand_keywords: string
  title_prompt_id: number
  content_prompt_id: number
  knowledge_ids: number[]
  image_category_id: number | null
  count: number
}

/** 生成文章 */
export function generateArticleApi(data: ArticleGenerateData): Promise<unknown> {
  return request.post('/api/articles/generate', data)
}

/** 获取文章列表 */
export function getArticlesApi(params: {
  page?: number
  page_size?: number
  status?: string
}): Promise<ArticleListResult> {
  return request.get('/api/articles', { params })
}

/** 获取文章详情 */
export function getArticleDetailApi(id: number): Promise<ArticleItem> {
  return request.get(`/api/articles/${id}`)
}

/** 更新文章 */
export function updateArticleApi(id: number, data: Partial<ArticleItem>): Promise<ArticleItem> {
  return request.put(`/api/articles/${id}`, data)
}

/** 删除文章 */
export function deleteArticleApi(id: number): Promise<void> {
  return request.delete(`/api/articles/${id}`)
}

/** 获取关键词列表（用于下拉选择） */
export function getKeywordsApi(): Promise<{ items: { id: number; keyword: string }[] }> {
  return request.get('/api/keywords', { params: { page: 1, page_size: 100 } })
}

/** 获取企业资料列表（用于下拉选择） */
export function getKnowledgeApi(): Promise<{ items: { id: number; title: string }[] }> {
  return request.get('/api/knowledge', { params: { page: 1, page_size: 100 } })
}

/** 获取图片分类列表（用于下拉选择） */
export function getImageCategoriesApi(): Promise<{ items: { id: number; name: string }[] }> {
  return request.get('/api/images/categories')
}
