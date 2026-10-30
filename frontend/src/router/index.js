import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn, isAdmin } from '../stores/auth'
import AdminLayout from '../layouts/AdminLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '概览' }
      },
      {
        path: 'banks',
        name: 'banks',
        component: () => import('../views/Bank.vue'),
        meta: { title: '题库管理', adminOnly: true }
      },
      {
        path: 'questions',
        name: 'questions',
        component: () => import('../views/Question.vue'),
        meta: { title: '题目管理', adminOnly: true }
      },
      {
        path: 'papers',
        name: 'papers',
        component: () => import('../views/Paper.vue'),
        meta: { title: '试卷管理', adminOnly: true }
      },
      {
        path: 'scores',
        name: 'scores',
        component: () => import('../views/Score.vue'),
        meta: { title: '成绩管理' }
      }
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
  if (to.meta.adminOnly && !isAdmin()) {
    return { path: '/scores' }
  }
  return true
})

export default router
