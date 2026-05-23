<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadProps } from 'element-plus'
import {
  getKnowledgeListApi,
  getKnowledgeDetailApi,
  deleteKnowledgeApi,
  uploadKnowledgeApi,
  type KnowledgeItem,
  type KnowledgeDetail
} from '@/api/knowledge'

const tableData = ref<KnowledgeItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)

// 详情弹窗
const detailVisible = ref(false)
const detailData = ref<KnowledgeDetail | null>(null)
const detailLoading = ref(false)

// 上传弹窗
const uploadVisible = ref(false)
const uploadLoading = ref(false)

/** 格式化文件大小 */
function formatSize(size: number): string {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

/** 加载列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await getKnowledgeListApi(currentPage.value, pageSize.value)
    tableData.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 查看详情 */
async function handleDetail(row: KnowledgeItem) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    detailData.value = await getKnowledgeDetailApi(row.id)
  } finally {
    detailLoading.value = false
  }
}
/** 删除 */
async function handleDelete(row: KnowledgeItem) {
  await ElMessageBox.confirm(`确定要删除文件「${row.file_name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await deleteKnowledgeApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

/** 上传前校验 */
const beforeUpload: UploadProps['beforeUpload'] = (rawFile) => {
  const allowTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
  const allowExts = ['.docx', '.pdf', '.txt']
  const ext = rawFile.name.substring(rawFile.name.lastIndexOf('.')).toLowerCase()
  if (!allowTypes.includes(rawFile.type) && !allowExts.includes(ext)) {
    ElMessage.error('仅支持上传 .docx / .pdf / .txt 文件')
    return false
  }
  return true
}

/** 自定义上传 */
async function handleUpload(options: { file: File }) {
  uploadLoading.value = true
  try {
    await uploadKnowledgeApi(options.file)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    loadList()
  } finally {
    uploadLoading.value = false
  }
}

onMounted(() => {
  loadList()
})
</script>

<template>
  <div class="knowledge-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <h2>企业资料管理</h2>
      <el-button type="primary" @click="uploadVisible = true">
        <el-icon><Upload /></el-icon>
        上传文件
      </el-button>
    </div>

    <!-- 表格 -->
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="file_name" label="文件名" min-width="200" />
        <el-table-column prop="file_type" label="文件类型" width="100" />
        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="上传时间" width="180">
          <template #default="{ row }">{{ row.created_at?.replace('T', ' ').slice(0, 19) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">查看详情</el-button>
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
    </el-card>
    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传企业资料" width="500px" destroy-on-close>
      <el-upload
        drag
        :auto-upload="true"
        :show-file-list="true"
        :before-upload="beforeUpload"
        :http-request="handleUpload"
        accept=".docx,.pdf,.txt"
      >
        <el-icon size="48" color="#409EFF"><Upload /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 .docx / .pdf / .txt 格式</div>
        </template>
      </el-upload>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="文件详情" width="700px" destroy-on-close>
      <div v-loading="detailLoading">
        <template v-if="detailData">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">{{ detailData.file_name }}</el-descriptions-item>
            <el-descriptions-item label="文件类型">{{ detailData.file_type }}</el-descriptions-item>
          </el-descriptions>
          <el-tabs style="margin-top: 16px">
            <el-tab-pane label="全文内容">
              <div class="content-text">{{ detailData.content_text }}</div>
            </el-tab-pane>
            <el-tab-pane label="分段列表">
              <el-collapse>
                <el-collapse-item
                  v-for="chunk in detailData.chunks"
                  :key="chunk.id"
                  :title="`段落 ${chunk.chunk_order}`"
                >
                  <p>{{ chunk.chunk_text }}</p>
                </el-collapse-item>
              </el-collapse>
            </el-tab-pane>
          </el-tabs>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.knowledge-page {
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

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.content-text {
  white-space: pre-wrap;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: var(--bg-page);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
