<script setup lang="ts">
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const stats = [
  { title: '文章总数', value: '--', icon: 'Document', color: '#6366f1' },
  { title: '核心主词', value: '--', icon: 'Key', color: '#10b981' },
  { title: '图片素材', value: '--', icon: 'Picture', color: '#f59e0b' },
  { title: 'AI指令', value: '--', icon: 'MagicStick', color: '#ef4444' }
]
</script>

<template>
  <div class="dashboard">
    <div class="welcome-section">
      <h2 class="welcome-title">
        欢迎回来，{{ userStore.userInfo?.username || '用户' }}
      </h2>
      <p class="welcome-desc">这是您的 GEO 营销系统工作台，祝您工作顺利</p>
    </div>

    <div class="stats-grid">
      <div v-for="item in stats" :key="item.title" class="stat-card">
        <div class="stat-icon" :style="{ backgroundColor: item.color + '12', color: item.color }">
          <el-icon size="24"><component :is="item.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.title }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 0;
}

.welcome-section {
  margin-bottom: 32px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px 0;
  letter-spacing: -0.02em;
}

.welcome-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
  font-weight: 500;
}
</style>
