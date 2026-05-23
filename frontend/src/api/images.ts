import request from './index'

export interface ImageCategory {
  id: number
  name: string
  related_keyword_id: number | null
  created_at: string
}

export interface ImageItem {
  id: number
  category_id: number
  file_url: string
  file_name: string
  file_size: number
  width: number
  height: number
  created_at: string
}

export interface ImageListResult {
  items: ImageItem[]
  total: number
}

/** 创建图片分类 */
export function createCategoryApi(data: { name: string; related_keyword_id?: number | null }): Promise<ImageCategory> {
  return request.post('/api/images/categories', data)
}

/** 获取图片分类列表 */
export function getCategoriesApi(): Promise<ImageCategory[]> {
  return request.get('/api/images/categories')
}

/** 更新图片分类 */
export function updateCategoryApi(id: number, data: { name: string }): Promise<ImageCategory> {
  return request.put(`/api/images/categories/${id}`, data)
}

/** 删除图片分类 */
export function deleteCategoryApi(id: number): Promise<void> {
  return request.delete(`/api/images/categories/${id}`)
}

/** 上传图片 */
export function uploadImageApi(categoryId: number, file: File): Promise<ImageItem> {
  const formData = new FormData()
  formData.append('category_id', String(categoryId))
  formData.append('file', file)
  return request.post('/api/images/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/** 获取分类下的图片列表 */
export function getCategoryImagesApi(categoryId: number, page: number, page_size: number): Promise<ImageListResult> {
  return request.get(`/api/images/categories/${categoryId}/images`, { params: { page, page_size } })
}

/** 删除图片 */
export function deleteImageApi(id: number): Promise<void> {
  return request.delete(`/api/images/${id}`)
}
