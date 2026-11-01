<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="login-title">赛博进京赶考</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" @keyup.enter="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="onSubmit">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-tip">演示账号：admin / admin123（管理员）、student01 / student123（考生）</div>
      <div class="login-switch">
        还没有账号？<router-link to="/register">注册一个</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'
import { setLoginInfo } from '../stores/auth'

const route = useRoute()
const router = useRouter()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function onSubmit() {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  loading.value = true
  try {
    const data = await login({ username: form.username, password: form.password })
    setLoginInfo(data)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect
    const home = data.role === 'ADMIN' ? '/dashboard' : '/exam-center'
    router.push(redirect ? String(redirect) : home)
  } catch (e) {
    // 错误提示已由 request 拦截器统一弹出
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: #fffef5;
  background-image: repeating-linear-gradient(
    transparent,
    transparent 27px,
    rgba(44, 44, 44, 0.12) 28px
  );
  background-size: 100% 28px;
}

.login-page::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 36px;
  width: 2px;
  background-color: #ff6b6b;
  pointer-events: none;
}

.login-card {
  width: 380px;
  padding: 12px 8px;
  border: 2px dashed #2c2c2c;
  border-radius: 4px;
  background-color: #fffef5;
  box-shadow: 6px 6px 0 #4ecdc4;
  transform: rotate(-1deg);
}

.login-title {
  position: relative;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
  margin: 0 0 24px;
  text-align: center;
  color: #2c2c2c;
}

.login-title::after {
  content: '';
  position: absolute;
  left: -4px;
  right: -4px;
  bottom: 2px;
  height: 0.45em;
  background-color: #ffd93d;
  z-index: -1;
}

.login-btn {
  width: 100%;
}

.login-switch {
  margin-top: 8px;
  text-align: center;
  color: rgba(44, 44, 44, 0.75);
  font-size: 13px;
}

.login-switch a {
  color: #2c2c2c;
  text-decoration: none;
  border-bottom: 2px dashed #ff6b6b;
  padding-bottom: 1px;
}

.login-switch a:hover {
  background-color: #ffd93d;
}
</style>
