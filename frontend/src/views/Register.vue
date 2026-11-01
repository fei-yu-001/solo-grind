<template>
  <div class="register-page">
    <el-card class="register-card">
      <h2 class="register-title">赛博进京赶考</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" @keyup.enter="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item prop="nickname">
          <el-input v-model="form.nickname" placeholder="昵称" size="large" />
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
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-btn"
            :loading="loading"
            @click="onSubmit"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-switch">
        已有账号？<router-link to="/login">去登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '../api/auth'

const router = useRouter()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

function validateConfirm(rule, value, callback) {
  if (!value) {
    callback(new Error('请再输入一次密码'))
    return
  }
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9_]{4,20}$/,
      message: '用户名需为 4-20 位字母、数字或下划线',
      trigger: 'blur'
    }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { max: 16, message: '昵称最多 16 个字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度需为 6-20 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再输入一次密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

async function onSubmit() {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  loading.value = true
  try {
    await register({
      username: form.username,
      nickname: form.nickname,
      password: form.password
    })
    ElMessage.success('注册成功，请登录')
    setTimeout(() => {
      router.push('/login')
    }, 1000)
  } catch (e) {
    // 错误提示已由 request 拦截器统一弹出
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
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

.register-page::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 36px;
  width: 2px;
  background-color: #ff6b6b;
  pointer-events: none;
}

.register-card {
  width: 400px;
  padding: 12px 8px;
  border: 2px dashed #2c2c2c;
  border-radius: 4px;
  background-color: #fffef5;
  box-shadow: 6px 6px 0 #4ecdc4;
  transform: rotate(1deg);
}

.register-title {
  position: relative;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
  margin: 0 0 24px;
  text-align: center;
  color: #2c2c2c;
}

.register-title::after {
  content: '';
  position: absolute;
  left: -4px;
  right: -4px;
  bottom: 2px;
  height: 0.45em;
  background-color: #ffd93d;
  z-index: -1;
}

.register-card :deep(.el-form-item) {
  margin-bottom: 18px;
}

.register-btn {
  width: 100%;
}

.register-switch {
  margin-top: 4px;
  text-align: center;
  color: rgba(44, 44, 44, 0.75);
  font-size: 13px;
}

.register-switch a {
  color: #2c2c2c;
  text-decoration: none;
  border-bottom: 2px dashed #ff6b6b;
  padding-bottom: 1px;
}

.register-switch a:hover {
  background-color: #ffd93d;
}
</style>