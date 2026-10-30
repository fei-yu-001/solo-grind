<template>
  <el-container class="layout">
    <el-aside width="200px" class="layout-aside">
      <div class="layout-logo">图书管理系统</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#001529"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/dashboard">统计概览</el-menu-item>
        <el-menu-item index="/books">图书管理</el-menu-item>
        <el-menu-item index="/categories">分类管理</el-menu-item>
        <el-menu-item index="/readers">读者管理</el-menu-item>
        <el-menu-item index="/borrows">借阅管理</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <span class="layout-title">{{ pageTitle }}</span>
        <span class="layout-user">
          <span class="layout-username">{{ realName || username }}</span>
          <el-button type="danger" link @click="onLogout">退出登录</el-button>
        </span>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { logout } from '../api/auth'
import { clearLoginInfo, getToken, getRealName } from '../stores/auth'

const route = useRoute()
const router = useRouter()

const realName = getRealName()
const username = getToken() ? 'admin' : ''

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '')

function onLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await logout()
      } catch (e) {
        // 后端不可达也照样清本地登录态
      }
      clearLoginInfo()
      ElMessage.success('已退出登录')
      router.push('/login')
    })
    .catch(() => {})
}
</script>

<style scoped>
.layout {
  height: 100%;
}

.layout-aside {
  background-color: #001529;
}

.layout-logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.layout-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.layout-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.layout-username {
  color: #606266;
  font-size: 14px;
}

.layout-main {
  padding: 0;
  background: #f5f7fa;
}
</style>
