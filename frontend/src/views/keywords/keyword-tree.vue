<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getKeywordDetailApi,
  generateKeywordTreeApi,
  getSubwordsApi,
  createSubwordApi,
  getCombinationsApi,
  createCombinationApi,
  deleteSubwordApi,
  deleteCombinationApi,
  type KeywordItem,
  type SubwordItem,
  type CombinationItem
} from '@/api/keywords'

const route = useRoute()
const router = useRouter()
const keywordId = Number(route.params.id)

// 核心主词信息
const keywordInfo = ref<KeywordItem | null>(null)

// 副词
const subwords = ref<SubwordItem[]>([])
const subwordsLoading = ref(false)
const selectedSubword = ref<SubwordItem | null>(null)
const newSubwordName = ref('')
const addingSubword = ref(false)

// 组合词
const combinations = ref<CombinationItem[]>([])
const combinationsLoading = ref(false)
const newComboWord = ref('')
const newComboIntent = ref('')
const addingCombo = ref(false)

// AI生成
const generating = ref(false)

// intent 选项
const intentOptions = ['推荐类', '厂商类', '采购类', '方案类', '场景类', '对比类', '问答类', '本地类']

// intent 颜色映射
const intentColorMap: Record<string, string> = {
  '推荐类': '#3b82f6',
  '厂商类': '#8b5cf6',
  '采购类': '#f97316',
  '方案类': '#10b981',
  '场景类': '#06b6d4',
  '对比类': '#eab308',
  '问答类': '#ec4899',
  '本地类': '#ef4444'
}

// 统计
const totalCombinations = computed(() => {
  return subwords.value.length > 0 ? subwords.value.length * 5 : 0 // 估算，实际按选中加载
})

/** 加载主词详情 */
async function loadKeywordInfo() {
  keywordInfo.value = await getKeywordDetailApi(keywordId)
}

/** 加载副词列表 */
async function loadSubwords() {
  subwordsLoading.value = true
  try {
    subwords.value = await getSubwordsApi(keywordId)
  } finally {
    subwordsLoading.value = false
  }
}

/** 选中副词 */
async function selectSubword(sw: SubwordItem) {
  selectedSubword.value = sw
  await loadCombinations(sw.id)
}

/** 加载组合词 */
async function loadCombinations(subwordId: number) {
  combinationsLoading.value = true
  try {
    combinations.value = await getCombinationsApi(subwordId)
  } finally {
    combinationsLoading.value = false
  }
}

/** AI生成关键词树 */
async function handleGenerate() {
  generating.value = true
  try {
    await generateKeywordTreeApi(keywordId)
    ElMessage.success('关键词树生成成功')
    await loadSubwords()
    if (subwords.value.length > 0) {
      await selectSubword(subwords.value[0])
    }
  } catch (_e: unknown) {
    // 错误已由拦截器处理
  } finally {
    generating.value = false
  }
}

/** 手动添加副词 */
async function handleAddSubword() {
  const name = newSubwordName.value.trim()
  if (!name) return
  addingSubword.value = true
  try {
    await createSubwordApi(keywordId, { name })
    ElMessage.success('添加成功')
    newSubwordName.value = ''
    await loadSubwords()
  } catch (_e: unknown) {
    // 错误已由拦截器处理
  } finally {
    addingSubword.value = false
  }
}

/** 手动添加组合词 */
async function handleAddCombo() {
  if (!selectedSubword.value) return
  const word = newComboWord.value.trim()
  if (!word) return
  addingCombo.value = true
  try {
    const data: { word: string; intent?: string } = { word }
    if (newComboIntent.value) data.intent = newComboIntent.value
    await createCombinationApi(selectedSubword.value.id, data)
    ElMessage.success('添加成功')
    newComboWord.value = ''
    newComboIntent.value = ''
    await loadCombinations(selectedSubword.value.id)
  } catch (_e: unknown) {
    // 错误已由拦截器处理
  } finally {
    addingCombo.value = false
  }
}
/** 删除副词 */
async function handleDeleteSubword(sw: SubwordItem) {
  await ElMessageBox.confirm(`确定要删除副词「${sw.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await deleteSubwordApi(sw.id)
    ElMessage.success('删除成功')
    if (selectedSubword.value?.id === sw.id) {
      selectedSubword.value = null
      combinations.value = []
    }
    await loadSubwords()
  } catch (_e: unknown) {
    // 错误已由拦截器处理
  }
}

/** 删除组合词 */
async function handleDeleteCombo(combo: CombinationItem) {
  await ElMessageBox.confirm(`确定要删除组合词「${combo.word}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await deleteCombinationApi(combo.id)
    ElMessage.success('删除成功')
    if (selectedSubword.value) {
      await loadCombinations(selectedSubword.value.id)
    }
  } catch (_e: unknown) {
    // 错误已由拦截器处理
  }
}

/** 获取intent颜色 */
function getIntentColor(intent: string | null): string {
  if (!intent) return '#6b7280'
  return intentColorMap[intent] || '#6b7280'
}

onMounted(async () => {
  await loadKeywordInfo()
  await loadSubwords()
  if (subwords.value.length > 0) {
    await selectSubword(subwords.value[0])
  }
})
</script>

<template>
  <div class="keyword-tree-page">
    <!-- 顶部面包屑 -->
    <div class="page-header">
      <div class="page-header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>
            <span class="breadcrumb-link" @click="router.push('/keywords')">核心主词管理</span>
          </el-breadcrumb-item>
          <el-breadcrumb-item>关键词树</el-breadcrumb-item>
        </el-breadcrumb>
        <h2 class="page-title">关键词树 - {{ keywordInfo?.keyword || '' }}</h2>
      </div>
      <el-button @click="router.push('/keywords')">
        <el-icon><Back /></el-icon> 返回
      </el-button>
    </div>

    <!-- 三栏布局 -->
    <div class="tree-layout">
      <!-- 左栏：核心主词信息 -->
      <div class="panel panel-left">
        <div class="info-card">
          <h3 class="panel-title">核心主词</h3>
          <div class="info-item">
            <span class="info-label">主词</span>
            <span class="info-value">{{ keywordInfo?.keyword || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">目标转化词</span>
            <span class="info-value">{{ keywordInfo?.target_word || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">行业</span>
            <span class="info-value">{{ keywordInfo?.industry || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">关联产品</span>
            <span class="info-value">{{ keywordInfo?.related_product || '-' }}</span>
          </div>
        </div>

        <el-button
          class="generate-btn"
          type="primary"
          :loading="generating"
          @click="handleGenerate"
        >
          <el-icon v-if="!generating"><MagicStick /></el-icon>
          {{ generating ? '' : 'AI 生成关键词树' }}
        </el-button>
        <p v-if="generating" class="generating-tip">AI正在生成，预计需要30-60秒...</p>

        <div class="stats-card">
          <div class="stat-item">
            <span class="stat-number">{{ subwords.length }}</span>
            <span class="stat-label">副词数量</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ combinations.length }}</span>
            <span class="stat-label">当前组合词</span>
          </div>
        </div>
      </div>
      <!-- 中栏：副词列表 -->
      <div class="panel panel-middle">
        <h3 class="panel-title">副词列表</h3>
        <div class="subword-list" v-loading="subwordsLoading">
          <div
            v-for="sw in subwords"
            :key="sw.id"
            class="subword-card"
            :class="{ active: selectedSubword?.id === sw.id }"
            @click="selectSubword(sw)"
          >
            <div class="subword-card-header">
              <span class="subword-name">{{ sw.name }}</span>
              <span
                v-if="sw.search_potential_score != null"
                class="subword-score"
              >{{ sw.search_potential_score }}</span>
            </div>
            <p v-if="sw.reason" class="subword-reason">{{ sw.reason }}</p>
            <div class="subword-card-footer">
              <el-tag
                :type="sw.source === 'ai' ? '' : 'warning'"
                size="small"
                effect="plain"
              >{{ sw.source === 'ai' ? 'AI' : '手动' }}</el-tag>
            </div>
            <el-icon
              class="subword-delete"
              @click.stop="handleDeleteSubword(sw)"
            ><Close /></el-icon>
          </div>
          <div v-if="!subwordsLoading && subwords.length === 0" class="empty-tip">
            暂无副词，请点击左侧"AI生成"或手动添加
          </div>
        </div>
        <div class="add-row">
          <el-input
            v-model="newSubwordName"
            placeholder="输入副词名称"
            size="small"
            @keyup.enter="handleAddSubword"
          />
          <el-button
            type="primary"
            size="small"
            :loading="addingSubword"
            :disabled="!newSubwordName.trim()"
            @click="handleAddSubword"
          >添加</el-button>
        </div>
      </div>
      <!-- 右栏：组合词列表 -->
      <div class="panel panel-right">
        <h3 class="panel-title">
          组合词列表
          <span v-if="selectedSubword" class="panel-subtitle"> - {{ selectedSubword.name }}</span>
        </h3>

        <div v-if="!selectedSubword" class="empty-state">
          <el-icon size="48" color="#d1d5db"><Connection /></el-icon>
          <p>请在左侧选择一个副词查看组合词</p>
        </div>

        <template v-else>
          <el-table
            :data="combinations"
            v-loading="combinationsLoading"
            style="width: 100%"
            size="small"
          >
            <el-table-column prop="word" label="组合词" min-width="180" />
            <el-table-column label="意图" width="100" align="center">
              <template #default="{ row }">
                <el-tag
                  v-if="row.intent"
                  size="small"
                  :style="{ backgroundColor: getIntentColor(row.intent) + '18', color: getIntentColor(row.intent), borderColor: getIntentColor(row.intent) + '40' }"
                >{{ row.intent }}</el-tag>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            <el-table-column label="优先级" width="80" align="center">
              <template #default="{ row }">
                <span v-if="row.priority != null">{{ row.priority }}</span>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            <el-table-column label="文章状态" width="100" align="center">
              <template #default="{ row }">
                <span>{{ row.article_status || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="来源" width="80" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.source === 'ai' ? '' : 'warning'"
                  size="small"
                  effect="plain"
                >{{ row.source === 'ai' ? 'AI' : '手动' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="70" align="center">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="handleDeleteCombo(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="add-combo-row">
            <el-input
              v-model="newComboWord"
              placeholder="输入组合词"
              size="small"
              class="combo-input"
              @keyup.enter="handleAddCombo"
            />
            <el-select
              v-model="newComboIntent"
              placeholder="意图"
              size="small"
              clearable
              class="combo-select"
            >
              <el-option
                v-for="opt in intentOptions"
                :key="opt"
                :label="opt"
                :value="opt"
              />
            </el-select>
            <el-button
              type="primary"
              size="small"
              :loading="addingCombo"
              :disabled="!newComboWord.trim()"
              @click="handleAddCombo"
            >添加</el-button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.keyword-tree-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.breadcrumb-link {
  cursor: pointer;
  color: var(--color-primary);
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

/* 三栏布局 */
.tree-layout {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.panel {
  background: var(--bg-card, #fff);
  border-radius: var(--radius-lg, 12px);
  border: 1px solid var(--border-color, #e2e8f0);
  padding: 20px;
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.05));
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-left {
  width: 280px;
  flex-shrink: 0;
  gap: 20px;
}

.panel-middle {
  width: 300px;
  flex-shrink: 0;
}

.panel-right {
  flex: 1;
  min-width: 400px;
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  margin: 0 0 16px 0;
}

.panel-subtitle {
  font-weight: 400;
  color: var(--text-secondary, #64748b);
}

/* 左栏信息卡片 */
.info-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.info-value {
  font-size: 14px;
  color: var(--text-primary, #1e293b);
  font-weight: 500;
  word-break: break-all;
}

.generate-btn {
  width: 100%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  border: none !important;
  font-weight: 600;
  height: 42px;
  font-size: 14px;
}

.generate-btn:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
}

.generating-tip {
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  text-align: center;
  margin: 8px 0 0 0;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.stats-card {
  display: flex;
  gap: 16px;
  padding: 12px 0 0 0;
  border-top: 1px solid var(--border-color, #e2e8f0);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary, #6366f1);
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  margin-top: 2px;
}

/* 中栏副词列表 */
.subword-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-right: 4px;
}

.subword-card {
  position: relative;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e2e8f0);
  cursor: pointer;
  transition: all 0.2s;
}

.subword-card:hover {
  border-color: var(--color-primary, #6366f1);
  background: #f8fafc;
}

.subword-card.active {
  border-color: var(--color-primary, #6366f1);
  border-left: 3px solid var(--color-primary, #6366f1);
  background: rgba(99, 102, 241, 0.04);
}

.subword-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subword-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
}

.subword-score {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  background: var(--color-primary, #6366f1);
  border-radius: 10px;
  padding: 2px 8px;
  min-width: 28px;
  text-align: center;
}

.subword-reason {
  font-size: 12px;
  color: var(--text-secondary, #64748b);
  margin: 6px 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.subword-card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.subword-delete {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 14px;
  color: #cbd5e1;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}

.subword-card:hover .subword-delete {
  opacity: 1;
}

.subword-delete:hover {
  color: #ef4444;
}

.empty-tip {
  text-align: center;
  color: var(--text-muted, #94a3b8);
  font-size: 13px;
  padding: 40px 0;
}

.add-row {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #e2e8f0);
}

/* 右栏组合词 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 12px;
  color: var(--text-muted, #94a3b8);
  font-size: 14px;
}

.text-muted {
  color: var(--text-muted, #94a3b8);
}

.add-combo-row {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #e2e8f0);
}

.combo-input {
  flex: 1;
}

.combo-select {
  width: 120px;
}
</style>
