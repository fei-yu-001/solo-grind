import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '../stores/auth'
import AdminLayout from '../layouts/AdminLayout.vue'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue'), meta: { title: '统计概览' } },
      { path: 'books', name: 'books', component: () => import('../views/BookView.vue'), meta: { title: '图书管理' } },
      { path: 'categories', name: 'categories', component: () => import('../views/CategoryView.vue'), meta: { title: '分类管理' } },
      { path: 'readers', name: 'readers', component: () => import('../views/ReaderView.vue'), meta: { title: '读者管理' } },
      { path: 'borrows', name: 'borrows', component: () => import('../views/BorrowView.vue'), meta: { title: '借阅管理' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  if (!to.meta.public && !isLoggedIn()) {
    return { path: '/login', query: to.fullPath === '/' ? {} : { redirect: to.fullPath } }
  }
  if (to.path === '/login' && isLoggedIn()) {
    return { path: '/' }
  }
})

export default router
