<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import {
  getKeywordsListApi,
  createKeywordApi,
  updateKeywordApi,
  deleteKeywordApi,
  generateExpansionsApi,
  getExpansionsApi,
  deleteExpansionApi,
  type KeywordItem,
  type KeywordForm,
  type ExpansionItem
} from '@/api/keywords'

const router = useRouter()

const tableData = ref<KeywordItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const searchKeyword = ref('')

// 弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('新增主词')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive<KeywordForm>({
  keyword: '',
  target_word: '',
  industry: '',
  related_product: ''
})

const formRules = {
  keyword: [{ required: true, message: '请输入主词', trigger: 'blur' }]
}

/** 加载列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await getKeywordsListApi({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value || undefined
    })
    tableData.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 搜索 */
function handleSearch() {
  currentPage.value = 1
  loadList()
}
/** 新增 */
function showAdd() {
  editingId.value = null
  dialogTitle.value = '新增主词'
  form.keyword = ''
  form.target_word = ''
  form.industry = ''
  form.related_product = ''
  dialogVisible.value = true
}

/** 编辑 */
function showEdit(row: KeywordItem) {
  editingId.value = row.id
  dialogTitle.value = '编辑主词'
  form.keyword = row.keyword
  form.target_word = row.target_word
  form.industry = row.industry
  form.related_product = row.related_product
  dialogVisible.value = true
}

/** 保存 */
async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate()
  if (editingId.value) {
    await updateKeywordApi(editingId.value, { ...form })
    ElMessage.success('修改成功')
  } else {
    await createKeywordApi({ ...form })
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadList()
}

/** 删除 */
async function handleDelete(row: KeywordItem) {
  await ElMessageBox.confirm(`确定要删除主词「${row.keyword}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await deleteKeywordApi(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch (e: any) {
    // 后端可能返回有关联文章的错误，已由拦截器显示
  }
}

/** 状态文本 */
function statusText(status: number): string {
  return status === 1 ? '启用' : '停用'
}

function statusType(status: number): string {
  return status === 1 ? 'success' : 'info'
}

// ========== 拓展词抽屉 ==========
const drawerVisible = ref(false)
const drawerKeyword = ref<KeywordItem | null>(null)
const expansionList = ref<ExpansionItem[]>([])
const expansionTotal = ref(0)
const expansionPage = ref(1)
const expansionPageSize = ref(50)
const expansionLoading = ref(false)
const generating = ref(false)

/** 打开拓展词抽屉 */
function showExpansions(row: KeywordItem) {
  drawerKeyword.value = row
  expansionPage.value = 1
  expansionList.value = []
  expansionTotal.value = 0
  drawerVisible.value = true
  loadExpansions()
}

/** 加载拓展词列表 */
async function loadExpansions() {
  if (!drawerKeyword.value) return
  expansionLoading.value = true
  try {
    const res = await getExpansionsApi(drawerKeyword.value.id, {
      page: expansionPage.value,
      page_size: expansionPageSize.value
    })
    expansionList.value = res.items
    expansionTotal.value = res.total
  } finally {
    expansionLoading.value = false
  }
}

/** AI生成拓展词 */
async function handleGenerate() {
  if (!drawerKeyword.value) return
  generating.value = true
  try {
    await generateExpansionsApi(drawerKeyword.value.id)
    ElMessage.success('拓展词生成成功')
    loadExpansions()
  } catch (e: any) {
    // 错误已由拦截器处理
  } finally {
    generating.value = false
  }
}

/** 删除拓展词 */
async function handleDeleteExpansion(row: ExpansionItem) {
  await ElMessageBox.confirm(`确定要删除拓展词「${row.phrase}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await deleteExpansionApi(row.id)
    ElMessage.success('删除成功')
    loadExpansions()
  } catch (e: any) {
    // 错误已由拦截器处理
  }
}

/** 拓展词类型标签 */
function phraseTypeLabel(type: string): string {
  return type === 'suffix' ? '副词' : type === 'combined' ? '组合词' : type
}

function phraseTypeTag(type: string): string {
  return type === 'suffix' ? '' : type === 'combined' ? 'success' : 'info'
}

onMounted(() => {
  loadList()
})
</script>

<template>
  <div class="keywords-page">
    <!-- Page header -->
    <div class="page-header">
      <div class="page-header-left">
        <h2 class="page-title">核心主词管理</h2>
        <p class="page-desc">管理您的核心关键词，生成拓展词用于文章创作</p>
      </div>
      <el-button type="primary" @click="showAdd">
        <el-icon><Plus /></el-icon> 新增主词
      </el-button>
    </div>

    <!-- Search bar -->
    <div class="search-area">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索主词..."
        clearable
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- Table card -->
    <div class="table-card">
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="keyword" label="主词" min-width="140" />
        <el-table-column prop="target_word" label="目标转化词" min-width="140" />
        <el-table-column prop="industry" label="行业" width="120" />
        <el-table-column prop="related_product" label="关联产品" width="140" />
        <el-table-column label="已生成文章数" width="120" align="center">
          <template #default="{ row }">{{ row.generated_article_count }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="success"
              link
              :disabled="!row.target_word"
              @click="router.push(`/keywords/${row.id}/tree`)"
            >关键词树</el-button>
            <el-button type="primary" link @click="showEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadList"
          @size-change="loadList"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="主词" prop="keyword">
          <el-input v-model="form.keyword" placeholder="请输入主词（必填）" />
        </el-form-item>
        <el-form-item label="目标转化词">
          <el-input v-model="form.target_word" placeholder="请输入目标转化词" />
        </el-form-item>
        <el-form-item label="行业">
          <el-input v-model="form.industry" placeholder="请输入行业" />
        </el-form-item>
        <el-form-item label="关联产品">
          <el-input v-model="form.related_product" placeholder="请输入关联产品" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 拓展词抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="`拓展词 - ${drawerKeyword?.keyword || ''}`"
      size="520px"
    >
      <div class="expansion-header">
        <el-button
          class="generate-btn"
          type="primary"
          :loading="generating"
          @click="handleGenerate"
        >
          <el-icon v-if="!generating"><MagicStick /></el-icon>
          {{ generating ? 'AI生成中...' : 'AI生成拓展词' }}
        </el-button>
        <span class="expansion-count">共 {{ expansionTotal }} 条</span>
      </div>

      <el-table
        :data="expansionList"
        v-loading="expansionLoading"
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="phrase" label="拓展词" min-width="180" />
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="phraseTypeTag(row.phrase_type)" size="small">
              {{ phraseTypeLabel(row.phrase_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="使用次数" width="80" align="center">
          <template #default="{ row }">{{ row.used_count }}</template>
        </el-table-column>
        <el-table-column label="操作" width="70" align="center">
          <template #default="{ row }">
            <el-button type="danger" link @click="handleDeleteExpansion(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="expansionTotal > expansionPageSize">
        <el-pagination
          v-model:current-page="expansionPage"
          :page-size="expansionPageSize"
          :total="expansionTotal"
          layout="total, prev, pager, next"
          @current-change="loadExpansions"
        />
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.keywords-page {
  height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.page-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.search-area {
  margin-bottom: 20px;
}

.search-input {
  max-width: 320px;
}

.table-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.expansion-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.expansion-count {
  font-size: 13px;
  color: var(--text-muted);
}

.generate-btn {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  border: none !important;
  font-weight: 500;
}

.generate-btn:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
}
</style>
