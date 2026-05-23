<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { onMounted } from 'vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const menuItems = [
  { path: '/dashboard', title: '首页', icon: 'HomeFilled' },
  { path: '/knowledge', title: '企业资料', icon: 'OfficeBuilding' },
  { path: '/images', title: '图片素材', icon: 'Picture' },
  { path: '/keywords', title: '核心主词', icon: 'Key' },
  { path: '/prompts', title: 'AI指令', icon: 'MagicStick' },
  { path: '/articles', title: '文章管理', icon: 'Document' }
]

function handleMenuSelect(path: string) {
  router.push(path)
}

function handleLogout() {
  userStore.logout()
}

onMounted(() => {
  if (userStore.token && !userStore.userInfo) {
    userStore.getUserInfo()
  }
})
</script>

<template>
  <div class="layout-wrapper">
    <!-- Sidebar -->
    <aside class="layout-sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <el-icon size="20" color="#6366f1"><Promotion /></el-icon>
        </div>
        <span class="logo-text">GEO</span>
      </div>

      <nav class="sidebar-nav">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
          @click="handleMenuSelect(item.path)"
        >
          <el-icon size="18"><component :is="item.icon" /></el-icon>
          <span class="nav-label">{{ item.title }}</span>
        </div>
      </nav>
    </aside>

    <!-- Main area -->
    <div class="layout-main-area">
      <!-- Header -->
      <header class="layout-header">
        <div class="header-left">
          <h1 class="header-title">{{ menuItems.find(m => m.path === route.path)?.title || '' }}</h1>
        </div>
        <div class="header-right">
          <div class="user-info">
            <div class="user-avatar">
              {{ (userStore.userInfo?.username || 'U').charAt(0).toUpperCase() }}
            </div>
            <span class="user-name">{{ userStore.userInfo?.username || '用户' }}</span>
          </div>
          <el-button text class="logout-btn" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
          </el-button>
        </div>
      </header>

      <!-- Content -->
      <main class="layout-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout-wrapper {
  display: flex;
  height: 100vh;
  width: 100%;
  background: var(--bg-page);
}

/* Sidebar */
.layout-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 0;
}

.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 10px;
  border-bottom: 1px solid var(--border-light);
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--color-primary-lighter);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.sidebar-nav {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin-bottom: 2px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  transition: var(--transition);
  font-size: 14px;
  font-weight: 500;
  position: relative;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--color-primary-lighter);
  color: var(--color-primary);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-primary);
  border-radius: 0 3px 3px 0;
}

.nav-label {
  white-space: nowrap;
}

/* Header */
.layout-main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-header {
  height: 64px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  flex-shrink: 0;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.logout-btn {
  color: var(--text-muted) !important;
  padding: 6px !important;
}

.logout-btn:hover {
  color: var(--color-danger) !important;
}

/* Content */
.layout-content {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
  background: var(--bg-page);
}
</style>
