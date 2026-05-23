<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getArticlesApi,
  generateArticleApi,
  getKeywordsApi,
  getKnowledgeApi,
  getImageCategoriesApi
} from '@/api/articles'
import type { ArticleItem } from '@/api/articles'
import { getPromptsApi } from '@/api/prompts'
import type { PromptItem } from '@/api/prompts'

const activeTab = ref('generate')

// --- 生成文章 Tab ---
const keywordOptions = ref<{ id: number; keyword: string }[]>([])
const titlePromptOptions = ref<PromptItem[]>([])
const contentPromptOptions = ref<PromptItem[]>([])
const knowledgeOptions = ref<{ id: number; title: string }[]>([])
const categoryOptions = ref<{ id: number; name: string }[]>([])
const generating = ref(false)

const generateForm = reactive({
  keyword_id: null as number | null,
  expand_keywords: '',
  title_prompt_id: null as number | null,
  content_prompt_id: null as number | null,
  knowledge_ids: [] as number[],
  image_category_id: null as number | null,
  count: 1
})

// --- 文章列表 Tab ---
const listLoading = ref(false)
const articleList = ref<ArticleItem[]>([])
const articleTotal = ref(0)

const listParams = reactive({
  page: 1,
  page_size: 10,
  status: ''
})

async function fetchArticles() {
  listLoading.value = true
  try {
    const params: Record<string, unknown> = {
      page: listParams.page,
      page_size: listParams.page_size
    }
    if (listParams.status) params.status = listParams.status
    const res = await getArticlesApi(params as Parameters<typeof getArticlesApi>[0])
    articleList.value = res.items
    articleTotal.value = res.total
  } catch {
    // API not yet implemented, show empty
    articleList.value = []
    articleTotal.value = 0
  } finally {
    listLoading.value = false
  }
}

function handleListSearch() {
  listParams.page = 1
  fetchArticles()
}

function handleListPageChange(page: number) {
  listParams.page = page
  fetchArticles()
}

async function handleGenerate() {
  if (!generateForm.keyword_id) {
    ElMessage.warning('请选择核心主词')
    return
  }
  if (!generateForm.title_prompt_id) {
    ElMessage.warning('请选择标题指令')
    return
  }
  if (!generateForm.content_prompt_id) {
    ElMessage.warning('请选择内容指令')
    return
  }
  generating.value = true
  try {
    await generateArticleApi({
      keyword_id: generateForm.keyword_id,
      expand_keywords: generateForm.expand_keywords,
      title_prompt_id: generateForm.title_prompt_id,
      content_prompt_id: generateForm.content_prompt_id,
      knowledge_ids: generateForm.knowledge_ids,
      image_category_id: generateForm.image_category_id,
      count: generateForm.count
    })
    ElMessage.success('文章生成任务已提交')
  } catch {
    ElMessage.warning('文章生成服务尚未部署，请先配置 One API')
  } finally {
    generating.value = false
  }
}

async function loadOptions() {
  try {
    const kwRes = await getKeywordsApi()
    keywordOptions.value = kwRes.items || []
  } catch { keywordOptions.value = [] }

  try {
    const titleRes = await getPromptsApi({ prompt_type: 'title', page: 1, page_size: 100 })
    titlePromptOptions.value = titleRes.items || []
  } catch { titlePromptOptions.value = [] }

  try {
    const contentRes = await getPromptsApi({ prompt_type: 'content', page: 1, page_size: 100 })
    contentPromptOptions.value = contentRes.items || []
  } catch { contentPromptOptions.value = [] }

  try {
    const knRes = await getKnowledgeApi()
    knowledgeOptions.value = knRes.items || []
  } catch { knowledgeOptions.value = [] }

  try {
    const catRes = await getImageCategoriesApi()
    categoryOptions.value = catRes.items || []
  } catch { categoryOptions.value = [] }
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = { review: '待审核', published: '已发布', rejected: '已拒绝' }
  return map[status] || status
}

function getStatusType(status: string) {
  const map: Record<string, string> = { review: 'warning', published: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

onMounted(() => {
  loadOptions()
  fetchArticles()
})
</script>

<template>
  <div class="articles-page">
    <h2 class="page-title">文章管理</h2>

    <el-tabs v-model="activeTab">
      <!-- Tab 1: 生成文章 -->
      <el-tab-pane label="生成文章" name="generate">
        <el-card shadow="never" class="generate-card">
          <el-form :model="generateForm" label-width="100px">
            <el-form-item label="核心主词">
              <el-select v-model="generateForm.keyword_id" placeholder="请选择核心主词" filterable style="width: 100%;">
                <el-option
                  v-for="item in keywordOptions"
                  :key="item.id"
                  :label="item.keyword"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="拓展关键词">
              <el-input v-model="generateForm.expand_keywords" placeholder="手动输入，多个关键词用逗号分隔" />
            </el-form-item>
            <el-form-item label="标题指令">
              <el-select v-model="generateForm.title_prompt_id" placeholder="请选择标题指令" style="width: 100%;">
                <el-option
                  v-for="item in titlePromptOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="内容指令">
              <el-select v-model="generateForm.content_prompt_id" placeholder="请选择内容指令" style="width: 100%;">
                <el-option
                  v-for="item in contentPromptOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="企业资料">
              <el-select v-model="generateForm.knowledge_ids" multiple placeholder="请选择企业资料" style="width: 100%;">
                <el-option
                  v-for="item in knowledgeOptions"
                  :key="item.id"
                  :label="item.title"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="图片分类">
              <el-select v-model="generateForm.image_category_id" placeholder="请选择图片分类" clearable style="width: 100%;">
                <el-option
                  v-for="item in categoryOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="生成数量">
              <el-input-number v-model="generateForm.count" :min="1" :max="10" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="generating" @click="handleGenerate">开始生成</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- Tab 2: 文章列表 -->
      <el-tab-pane label="文章列表" name="list">
        <el-card shadow="never">
          <el-row :gutter="16" align="middle" class="filter-row">
            <el-col :span="5">
              <el-select v-model="listParams.status" placeholder="状态筛选" clearable @change="handleListSearch">
                <el-option label="全部" value="" />
                <el-option label="待审核" value="review" />
                <el-option label="已发布" value="published" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-col>
            <el-col :span="3">
              <el-button type="primary" @click="handleListSearch">搜索</el-button>
            </el-col>
          </el-row>

          <el-table :data="articleList" v-loading="listLoading" style="width: 100%;">
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="keyword" label="核心主词" width="130" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status) as any" size="small">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="生成时间" width="170" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default>
                <el-button type="primary" text size="small">查看</el-button>
                <el-button type="primary" text size="small">编辑</el-button>
                <el-button type="danger" text size="small">删除</el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无文章数据" />
            </template>
          </el-table>

          <div class="pagination-wrap">
            <el-pagination
              v-model:current-page="listParams.page"
              :page-size="listParams.page_size"
              :total="articleTotal"
              layout="total, prev, pager, next"
              @current-change="handleListPageChange"
            />
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.articles-page {
  padding: 0;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
  letter-spacing: -0.02em;
}

.generate-card {
  max-width: 700px;
}

.filter-row {
  margin-bottom: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
