<template>
  <el-container class="layout">
    <el-aside width="200px" class="layout-aside">
      <div class="layout-logo">智考刷题系统</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#fffef5"
        text-color="#2c2c2c"
        active-text-color="#2c2c2c"
      >
        <template v-for="item in menus" :key="item.path">
          <el-menu-item :index="item.path">{{ item.title }}</el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <span class="layout-title">{{ pageTitle }}</span>
        <span class="layout-user">
          <span class="layout-username">{{ nickname || username }}</span>
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
import { clearLoginInfo, getLoginUser } from '../stores/auth'

const route = useRoute()
const router = useRouter()

const allMenus = [
  { path: '/dashboard', title: '概览', adminOnly: true },
  { path: '/banks', title: '题库', adminOnly: true },
  { path: '/questions', title: '题目', adminOnly: true },
  { path: '/papers', title: '试卷', adminOnly: true },
  { path: '/scores', title: '成绩', adminOnly: true },
  { path: '/exam-center', title: '考试中心', adminOnly: false, studentOnly: true },
  { path: '/my-scores', title: '我的成绩', adminOnly: true, studentOnly: true }
]

const user = getLoginUser()
const nickname = (user && user.nickname) || ''
const username = (user && user.username) || ''
const isAdmin = (user && user.role) === 'ADMIN'

const menus = allMenus.filter((item) => {
  if (isAdmin) {
    return !item.studentOnly || item.path === '/exam-center'
  }
  return !item.adminOnly
})
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
  background-color: #fffef5;
  border-right: 2px dashed #2c2c2c;
}

.layout-logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  position: relative;
  color: #2c2c2c;
  font-size: 16px;
  font-weight: 600;
}

.layout-logo::after {
  content: '';
  position: absolute;
  left: 14%;
  right: 14%;
  bottom: 12px;
  height: 8px;
  background-color: #ffd93d;
  z-index: -1;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fffef5;
  border-bottom: 2px dashed #2c2c2c;
}

.layout-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c2c2c;
}

.layout-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.layout-username {
  color: rgba(44, 44, 44, 0.75);
  font-size: 14px;
}

.layout-main {
  padding: 0;
  background: #fffef5;
}
</style>
