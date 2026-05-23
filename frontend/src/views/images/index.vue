<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getCategoriesApi,
  createCategoryApi,
  updateCategoryApi,
  deleteCategoryApi,
  getCategoryImagesApi,
  uploadImageApi,
  deleteImageApi,
  type ImageCategory,
  type ImageItem
} from '@/api/images'

const BASE_URL = 'http://127.0.0.1:8000/'

// 分类
const categories = ref<ImageCategory[]>([])
const activeCategoryId = ref<number | null>(null)
const categoryDialogVisible = ref(false)
const categoryForm = ref({ name: '' })
const editingCategoryId = ref<number | null>(null)

// 图片
const images = ref<ImageItem[]>([])
const imageTotal = ref(0)
const imagePage = ref(1)
const imagePageSize = ref(20)
const imageLoading = ref(false)

// 预览
const previewVisible = ref(false)
const previewUrl = ref('')

const activeCategory = computed(() => {
  return categories.value.find(c => c.id === activeCategoryId.value)
})

/** 加载分类列表 */
async function loadCategories() {
  categories.value = await getCategoriesApi()
  if (categories.value.length > 0 && !activeCategoryId.value) {
    activeCategoryId.value = categories.value[0].id
    loadImages()
  }
}

/** 选择分类 */
function handleSelectCategory(id: number) {
  activeCategoryId.value = id
  imagePage.value = 1
  loadImages()
}
/** 加载图片列表 */
async function loadImages() {
  if (!activeCategoryId.value) return
  imageLoading.value = true
  try {
    const res = await getCategoryImagesApi(activeCategoryId.value, imagePage.value, imagePageSize.value)
    images.value = res.items
    imageTotal.value = res.total
  } finally {
    imageLoading.value = false
  }
}

/** 新增分类弹窗 */
function showAddCategory() {
  editingCategoryId.value = null
  categoryForm.value = { name: '' }
  categoryDialogVisible.value = true
}

/** 编辑分类弹窗 */
function showEditCategory(cat: ImageCategory) {
  editingCategoryId.value = cat.id
  categoryForm.value = { name: cat.name }
  categoryDialogVisible.value = true
}

/** 保存分类 */
async function handleSaveCategory() {
  if (!categoryForm.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  if (editingCategoryId.value) {
    await updateCategoryApi(editingCategoryId.value, { name: categoryForm.value.name })
    ElMessage.success('修改成功')
  } else {
    await createCategoryApi({ name: categoryForm.value.name })
    ElMessage.success('创建成功')
  }
  categoryDialogVisible.value = false
  loadCategories()
}

/** 删除分类 */
async function handleDeleteCategory(cat: ImageCategory) {
  await ElMessageBox.confirm(`确定要删除分类「${cat.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await deleteCategoryApi(cat.id)
  ElMessage.success('删除成功')
  if (activeCategoryId.value === cat.id) {
    activeCategoryId.value = null
    images.value = []
  }
  loadCategories()
}

/** 上传图片 */
async function handleUploadImage(options: { file: File }) {
  if (!activeCategoryId.value) {
    ElMessage.warning('请先选择分类')
    return
  }
  try {
    await uploadImageApi(activeCategoryId.value, options.file)
    ElMessage.success('上传成功')
    loadImages()
  } catch (e) {
    // error handled by interceptor
  }
}

/** 删除图片 */
async function handleDeleteImage(img: ImageItem) {
  await ElMessageBox.confirm('确定要删除这张图片吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await deleteImageApi(img.id)
  ElMessage.success('删除成功')
  loadImages()
}

/** 预览图片 */
function handlePreview(img: ImageItem) {
  previewUrl.value = BASE_URL + img.file_url
  previewVisible.value = true
}

/** 获取图片完整URL */
function getImageUrl(img: ImageItem): string {
  return BASE_URL + img.file_url
}

onMounted(() => {
  loadCategories()
})
</script>

<template>
  <div class="images-page">
    <div class="page-header">
      <h2>图片素材管理</h2>
    </div>
    <div class="images-content">
      <!-- 左侧分类 -->
      <div class="category-panel">
        <div class="category-header">
          <span>图片分类</span>
          <el-button type="primary" link @click="showAddCategory">
            <el-icon><Plus /></el-icon> 新增
          </el-button>
        </div>
        <div class="category-list">
          <div
            v-for="cat in categories"
            :key="cat.id"
            class="category-item"
            :class="{ active: activeCategoryId === cat.id }"
            @click="handleSelectCategory(cat.id)"
          >
            <span class="category-name">{{ cat.name }}</span>
            <span class="category-actions" @click.stop>
              <el-button type="primary" link size="small" @click="showEditCategory(cat)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteCategory(cat)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </span>
          </div>
          <el-empty v-if="categories.length === 0" description="暂无分类" :image-size="60" />
        </div>
      </div>

      <!-- 右侧图片区 -->
      <div class="image-panel">
        <div class="image-toolbar">
          <span v-if="activeCategory">{{ activeCategory.name }} ({{ imageTotal }}张)</span>
          <el-upload
            :auto-upload="true"
            :show-file-list="false"
            :http-request="handleUploadImage"
            accept="image/*"
          >
            <el-button type="primary" :disabled="!activeCategoryId">
              <el-icon><Upload /></el-icon> 上传图片
            </el-button>
          </el-upload>
        </div>

        <div v-loading="imageLoading" class="image-grid">
          <div v-for="img in images" :key="img.id" class="image-card">
            <el-image
              :src="getImageUrl(img)"
              fit="cover"
              class="image-thumb"
              @click="handlePreview(img)"
            />
            <div class="image-info">
              <span class="image-name" :title="img.file_name">{{ img.file_name }}</span>
              <el-button type="danger" link size="small" @click="handleDeleteImage(img)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <el-empty v-if="!imageLoading && images.length === 0" description="暂无图片" />
        </div>

        <div class="pagination-wrap" v-if="imageTotal > imagePageSize">
          <el-pagination
            v-model:current-page="imagePage"
            :page-size="imagePageSize"
            :total="imageTotal"
            layout="prev, pager, next"
            @current-change="loadImages"
          />
        </div>
      </div>
    </div>

    <!-- 分类弹窗 -->
    <el-dialog v-model="categoryDialogVisible" :title="editingCategoryId ? '编辑分类' : '新增分类'" width="400px">
      <el-form label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory">确定</el-button>
      </template>
    </el-dialog>

    <!-- 图片预览 -->
    <el-dialog v-model="previewVisible" title="图片预览" width="auto" destroy-on-close>
      <img :src="previewUrl" style="max-width: 100%; max-height: 70vh;" />
    </el-dialog>
  </div>
</template>

<style scoped>
.images-page {
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.images-content {
  display: flex;
  gap: 20px;
  height: calc(100% - 70px);
}

.category-panel {
  width: 240px;
  flex-shrink: 0;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-light);
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.category-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: var(--transition);
  border-radius: var(--radius-md);
  margin-bottom: 2px;
}

.category-item:hover {
  background: var(--bg-hover);
}

.category-item.active {
  background: var(--color-primary-lighter);
  color: var(--color-primary);
}

.category-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  font-size: 14px;
}

.category-actions {
  display: flex;
  gap: 4px;
}

.image-panel {
  flex: 1;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
}

.image-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-weight: 500;
  color: var(--text-secondary);
}

.image-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  align-content: start;
  overflow-y: auto;
}

.image-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: var(--transition);
}

.image-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.image-thumb {
  width: 100%;
  height: 150px;
  cursor: pointer;
  display: block;
}

.image-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
}

.image-name {
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
