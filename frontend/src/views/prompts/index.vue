<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Delete } from '@element-plus/icons-vue'
import {
  getPromptsApi,
  createPromptApi,
  updatePromptApi,
  deletePromptApi,
  batchDeletePromptsApi
} from '@/api/prompts'
import type { PromptItem, PromptCreateData } from '@/api/prompts'

// ========== 常量 ==========
const platformOptions = [
  '通用类', '百家号', '网易', '头条号', '公众号', '知乎', '搜狐', '抖音', '小红书', 'CSDN', 'B站'
]

const promptTypeOptions = [
  { label: '标题指令', value: 'title' },
  { label: '内容指令', value: 'content' },
  { label: '融合创作指令', value: 'fusion' }
]

const promptTypeMap: Record<string, string> = {
  title: '标题指令',
  content: '内容指令',
  fusion: '融合创作指令'
}

// ========== 列表数据 ==========
const loading = ref(false)
const tableData = ref<PromptItem[]>([])
const total = ref(0)
const selectedRows = ref<PromptItem[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 10,
  name: '',
  platform: '',
  prompt_type: '',
  start_date: '',
  end_date: ''
})

// ========== 弹窗状态 ==========
const dialogVisible = ref(false)
const dialogTitle = ref('添加指令规则')
const editingId = ref<number | null>(null)

const formData = reactive<PromptCreateData>({
  name: '',
  prompt_type: 'title',
  platform: '',
  prompt_text: ''
})

// 查看内容弹窗
const viewDialogVisible = ref(false)
const viewDialogTitle = ref('')
const viewContent = ref('')

// ========== 计算属性 ==========
const hasSelection = computed(() => selectedRows.value.length > 0)

// ========== 方法 ==========
async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: queryParams.page,
      page_size: queryParams.page_size
    }
    if (queryParams.name) params.name = queryParams.name
    if (queryParams.platform) params.platform = queryParams.platform
    if (queryParams.prompt_type) params.prompt_type = queryParams.prompt_type
    if (queryParams.start_date) params.start_date = queryParams.start_date
    if (queryParams.end_date) params.end_date = queryParams.end_date
    const res = await getPromptsApi(params as any)
    tableData.value = res.items
    total.value = res.total
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  queryParams.page = 1
  fetchData()
}

function handleReset() {
  queryParams.name = ''
  queryParams.platform = ''
  queryParams.prompt_type = ''
  queryParams.start_date = ''
  queryParams.end_date = ''
  queryParams.page = 1
  fetchData()
}

function handlePageChange(page: number) {
  queryParams.page = page
  fetchData()
}

function handleSizeChange(size: number) {
  queryParams.page_size = size
  queryParams.page = 1
  fetchData()
}

function handleSelectionChange(rows: PromptItem[]) {
  selectedRows.value = rows
}

// ========== 查看内容 ==========
function handleViewContent(row: PromptItem) {
  viewDialogTitle.value = `指令内容 - ${row.name}`
  viewContent.value = row.prompt_text
  viewDialogVisible.value = true
}

// ========== 新增/编辑 ==========
function openCreateDialog() {
  dialogTitle.value = '添加指令规则'
  editingId.value = null
  formData.name = ''
  formData.prompt_type = 'title'
  formData.platform = ''
  formData.prompt_text = ''
  dialogVisible.value = true
}

function openEditDialog(row: PromptItem) {
  dialogTitle.value = '编辑指令规则'
  editingId.value = row.id
  formData.name = row.name
  formData.prompt_type = row.prompt_type
  formData.platform = row.platform || ''
  formData.prompt_text = row.prompt_text
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formData.name.trim()) {
    ElMessage.warning('请输入指令名称')
    return
  }
  if (!formData.platform) {
    ElMessage.warning('请选择媒体平台')
    return
  }
  if (!formData.prompt_type) {
    ElMessage.warning('请选择创作类型')
    return
  }
  if (!formData.prompt_text.trim()) {
    ElMessage.warning('请输入指令内容')
    return
  }
  try {
    if (editingId.value) {
      await updatePromptApi(editingId.value, { ...formData })
      ElMessage.success('更新成功')
    } else {
      await createPromptApi({ ...formData })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch {
    // error handled by interceptor
  }
}

// ========== 删除 ==========
async function handleDelete(row: PromptItem) {
  try {
    await ElMessageBox.confirm('确定要删除该指令规则吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deletePromptApi(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {
    // cancelled or error
  }
}

async function handleBatchDelete() {
  if (!hasSelection.value) return
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条指令规则吗？`,
      '批量删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    const ids = selectedRows.value.map(r => r.id)
    await batchDeletePromptsApi(ids)
    ElMessage.success('批量删除成功')
    fetchData()
  } catch {
    // cancelled or error
  }
}

// ========== 工具函数 ==========
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  return dateStr.replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="prompts-page">
    <!-- 筛选区 -->
    <div class="filter-area">
      <el-input
        v-model="queryParams.name"
        placeholder="指令名称"
        clearable
        class="filter-item filter-input"
        @keyup.enter="handleSearch"
      />
      <el-select
        v-model="queryParams.platform"
        placeholder="发布平台"
        clearable
        class="filter-item"
      >
        <el-option
          v-for="p in platformOptions"
          :key="p"
          :label="p"
          :value="p"
        />
      </el-select>
      <el-select
        v-model="queryParams.prompt_type"
        placeholder="创作类型"
        clearable
        class="filter-item"
      >
        <el-option
          v-for="t in promptTypeOptions"
          :key="t.value"
          :label="t.label"
          :value="t.value"
        />
      </el-select>
      <el-date-picker
        v-model="queryParams.start_date"
        type="date"
        placeholder="开始日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        class="filter-item"
      />
      <el-date-picker
        v-model="queryParams.end_date"
        type="date"
        placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        class="filter-item"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button :icon="Refresh" circle @click="fetchData" />
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">添加指令规则</el-button>
      <el-button type="danger" :icon="Delete" :disabled="!hasSelection" @click="handleBatchDelete">批量删除</el-button>
      <el-button disabled>创建融合任务</el-button>
      <el-button disabled>导入</el-button>
      <el-button disabled>导出</el-button>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column type="index" label="序号" width="65" />
        <el-table-column prop="name" label="指令名称" min-width="160" />
        <el-table-column label="指令内容" min-width="120">
          <template #default="{ row }">
            <span class="view-content-link" @click="handleViewContent(row)">查看内容</span>
          </template>
        </el-table-column>
        <el-table-column label="发布平台" width="110">
          <template #default="{ row }">
            {{ row.platform || '通用类' }}
          </template>
        </el-table-column>
        <el-table-column label="创作类型" width="120">
          <template #default="{ row }">
            {{ promptTypeMap[row.prompt_type] || row.prompt_type }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <template v-if="row.is_default">
              <span class="readonly-text">只读</span>
            </template>
            <template v-else>
              <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- 查看内容弹窗 -->
    <el-dialog v-model="viewDialogVisible" :title="viewDialogTitle" width="650px" destroy-on-close>
      <div class="view-content-body">{{ viewContent }}</div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="620px" destroy-on-close>
      <el-form :model="formData" label-width="90px">
        <el-form-item label="指令名称" required>
          <el-input v-model="formData.name" placeholder="请输入指令名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="媒体平台" required>
          <el-select v-model="formData.platform" placeholder="请选择媒体平台" style="width: 100%;">
            <el-option
              v-for="p in platformOptions"
              :key="p"
              :label="p"
              :value="p"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创作类型" required>
          <el-select v-model="formData.prompt_type" placeholder="请选择创作类型" style="width: 100%;">
            <el-option
              v-for="t in promptTypeOptions"
              :key="t.value"
              :label="t.label"
              :value="t.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="指令内容" required>
          <el-input
            v-model="formData.prompt_text"
            type="textarea"
            :rows="10"
            maxlength="3000"
            show-word-limit
            placeholder="请输入AI指令内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.prompts-page {
  height: 100%;
}

.filter-area {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.filter-item {
  width: 160px;
}

.filter-input {
  width: 180px;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.table-card {
  background: var(--bg-card, #fff);
  border-radius: var(--radius-lg, 8px);
  border: 1px solid var(--border-color, #e4e7ed);
  padding: 20px;
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.05));
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.view-content-link {
  color: var(--color-primary, #409eff);
  cursor: pointer;
  font-size: 14px;
}

.view-content-link:hover {
  text-decoration: underline;
}

.readonly-text {
  color: #909399;
  font-size: 13px;
}

.view-content-body {
  background: #fff;
  border: 1px solid var(--border-color, #e4e7ed);
  border-radius: 6px;
  padding: 16px;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.7;
  max-height: 400px;
  overflow-y: auto;
}
</style>
