<template>
  <div class="page">
    <el-card class="profile-card">
      <template #header>
        <span class="profile-title">个人资料</span>
      </template>
      <el-form ref="formRef" v-loading="loading" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="账号">
          <span>{{ account.username }}</span>
          <el-tag class="role-tag" size="small">{{ account.role === 'ADMIN' ? '管理员' : '考生' }}</el-tag>
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" maxlength="32" />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="form.school" maxlength="64" placeholder="可选" />
        </el-form-item>
        <el-form-item label="组别">
          <el-input v-model="form.groupName" maxlength="16" placeholder="可选，例如：本科组" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" maxlength="11" placeholder="可选" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getProfile, updateProfile } from '../api/profile'
import { getLoginUser, setLoginInfo, getToken } from '../stores/auth'

const formRef = ref()
const loading = ref(false)
const saving = ref(false)
const account = reactive({ username: '', role: '' })
const form = reactive({ nickname: '', school: '', groupName: '', phone: '' })

const rules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  phone: [{ pattern: /^$|^1[0-9]{10}$/, message: '手机号必须是 11 位数字', trigger: 'blur' }]
}

function fill(data) {
  account.username = data.username
  account.role = data.role
  form.nickname = data.nickname || ''
  const p = data.profile || {}
  form.school = p.school || ''
  form.groupName = p.groupName || ''
  form.phone = p.phone || ''
}

async function load() {
  loading.value = true
  try {
    fill(await getProfile())
  } finally {
    loading.value = false
  }
}

async function onSave() {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  saving.value = true
  try {
    const data = await updateProfile({ ...form })
    fill(data)
    // 同步本地登录信息里的昵称，顶栏立即更新
    setLoginInfo({ ...getLoginUser(), token: getToken(), nickname: data.nickname })
    ElMessage.success('资料已保存')
    setTimeout(() => window.location.reload(), 300)
  } catch (e) {
    // 错误提示已由 request 拦截器统一弹出
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.profile-card {
  max-width: 560px;
}

.profile-title {
  font-weight: 600;
}

.role-tag {
  margin-left: 10px;
}
</style>
