import request from './index'

export interface KeywordItem {
  id: number
  keyword: string
  target_word: string
  industry: string
  related_product: string
  status: number
  generated_article_count: number
  created_at: string
  updated_at: string
}

export interface KeywordListResult {
  items: KeywordItem[]
  total: number
}

export interface KeywordForm {
  keyword: string
  target_word?: string
  industry?: string
  related_product?: string
}

/** 创建主词 */
export function createKeywordApi(data: KeywordForm): Promise<KeywordItem> {
  return request.post('/api/keywords', data)
}

/** 获取主词列表 */
export function getKeywordsListApi(params: { page: number; page_size: number; keyword?: string }): Promise<KeywordListResult> {
  return request.get('/api/keywords', { params })
}

/** 获取主词详情 */
export function getKeywordDetailApi(id: number): Promise<KeywordItem> {
  return request.get(`/api/keywords/${id}`)
}

/** 更新主词 */
export function updateKeywordApi(id: number, data: KeywordForm): Promise<KeywordItem> {
  return request.put(`/api/keywords/${id}`, data)
}

/** 删除主词 */
export function deleteKeywordApi(id: number): Promise<void> {
  return request.delete(`/api/keywords/${id}`)
}

// ========== 拓展词相关 ==========

export interface ExpansionItem {
  id: number
  phrase: string
  phrase_type: string
  source: string
  used_count: number
  created_at: string
}

export interface ExpansionListResult {
  items: ExpansionItem[]
  total: number
}

export interface GenerateExpansionsResult {
  core_keyword: string
  target_word: string
  sub_keywords: string[]
  combined_keywords: string[]
}

/** AI生成拓展词 */
export function generateExpansionsApi(keywordId: number): Promise<GenerateExpansionsResult> {
  return request.post(`/api/keywords/${keywordId}/expansions/generate`, null, { timeout: 60000 })
}

/** 查询拓展词列表 */
export function getExpansionsApi(keywordId: number, params: { page: number; page_size: number }): Promise<ExpansionListResult> {
  return request.get(`/api/keywords/${keywordId}/expansions`, { params })
}

/** 删除单条拓展词 */
export function deleteExpansionApi(expansionId: number): Promise<void> {
  return request.delete(`/api/keywords/expansions/${expansionId}`)
}

// ========== 关键词树相关 ==========

export interface SubwordItem {
  id: number
  core_keyword_id: number
  name: string
  reason: string | null
  search_potential_score: number | null
  source: string
  status: number
  created_at: string
}

export interface CombinationItem {
  id: number
  subword_id: number
  word: string
  intent: string | null
  priority: number | null
  source: string
  article_status: string | null
  created_at: string
}

export interface GenerateTreeResult {
  sub_words: {
    name: string
    reason: string
    search_potential_score: number
    combo_words: { word: string; intent: string; priority: number }[]
  }[]
}

/** AI生成关键词树 */
export function generateKeywordTreeApi(keywordId: number): Promise<GenerateTreeResult> {
  return request.post(`/api/keywords/${keywordId}/generate-tree`, null, { timeout: 90000 })
}

/** 获取副词列表 */
export function getSubwordsApi(keywordId: number): Promise<SubwordItem[]> {
  return request.get(`/api/keywords/${keywordId}/subwords`)
}

/** 手动添加副词 */
export function createSubwordApi(keywordId: number, data: { name: string }): Promise<SubwordItem> {
  return request.post(`/api/keywords/${keywordId}/subwords`, data)
}

/** 获取组合词列表 */
export function getCombinationsApi(subwordId: number): Promise<CombinationItem[]> {
  return request.get(`/api/keywords/subwords/${subwordId}/combinations`)
}

/** 手动添加组合词 */
export function createCombinationApi(subwordId: number, data: { word: string; intent?: string }): Promise<CombinationItem> {
  return request.post(`/api/keywords/subwords/${subwordId}/combinations`, data)
}

/** 删除副词 */
export function deleteSubwordApi(subwordId: number): Promise<void> {
  return request.delete(`/api/keywords/subwords/${subwordId}`)
}

/** 删除组合词 */
export function deleteCombinationApi(combinationId: number): Promise<void> {
  return request.delete(`/api/keywords/combinations/${combinationId}`)
}
