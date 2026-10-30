<template>
  <div class="page">
    <el-alert
      title="交卷后不能重考，进入考场前请确认时间充裕。"
      type="warning"
      show-icon
      :closable="false"
      class="center-tip"
    />
    <el-row :gutter="16">
      <el-col v-for="exam in exams" :key="exam.paperId" :span="12">
        <el-card class="exam-card">
          <div class="exam-title">{{ exam.title }}</div>
          <div class="exam-meta">
            <span>题库：{{ exam.bankName }}</span>
            <span>题量：{{ exam.questionCount }}</span>
            <span>总分：{{ exam.totalScore }}</span>
            <span>时长：{{ Math.round(exam.durationSec / 60) }} 分钟</span>
          </div>
          <div class="exam-footer">
            <template v-if="exam.myScore !== null && exam.myScore !== undefined">
              <el-tag type="success">已交卷</el-tag>
              <span class="exam-score">得分：{{ exam.myScore }}</span>
              <span class="exam-time">交卷时间：{{ exam.mySubmittedAt }}</span>
              <el-button type="primary" plain @click="viewScore(exam)">查看成绩</el-button>
            </template>
            <template v-else>
              <el-tag type="info">未交卷</el-tag>
              <el-button type="primary" @click="enterExam(exam)">进入考场</el-button>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="!loading && exams.length === 0" description="暂无可参加的考试" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getAvailableExams } from '../api/exams'
import { getLoginUser } from '../stores/auth'

const router = useRouter()
const loading = ref(true)
const exams = ref([])

function enterExam(exam) {
  router.push(`/exam/${exam.paperId}`)
}

function viewScore(exam) {
  const user = getLoginUser()
  router.push({
    path: '/my-scores',
    query: { paperId: exam.paperId, userId: user ? user.id : '' }
  })
}

onMounted(async () => {
  try {
    const list = await getAvailableExams()
    exams.value = list || []
  } catch (e) {
    // 错误提示已由 request 拦截器统一弹出
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.center-tip {
  margin-bottom: 16px;
}

.exam-card {
  margin-bottom: 16px;
}

.exam-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.exam-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: #606266;
  font-size: 14px;
  margin-bottom: 14px;
}

.exam-footer {
  display: flex;
  align-items: center;
  gap: 12px;
}

.exam-score {
  color: #303133;
  font-weight: 600;
}

.exam-time {
  color: #909399;
  font-size: 13px;
}
</style>
