<template>
  <div class="exam-room">
    <div class="exam-header">
      <span class="exam-title">{{ paper.title }}</span>
      <div class="exam-header-right">
        <span class="exam-timer" :class="{ danger: remaining <= 300 }">
          剩余时间 {{ formatTime(remaining) }}
        </span>
        <span class="exam-progress">已答 {{ answeredCount }} / {{ questions.length }} 题</span>
        <el-button type="primary" :loading="submitting" @click="onSubmitClick">交卷</el-button>
      </div>
    </div>
    <div class="exam-body">
      <div class="exam-main">
        <template v-if="current">
          <div class="q-head">
            <el-tag>{{ current.typeText }}</el-tag>
            <span class="q-seq">第 {{ current.seq }} 题 / 共 {{ questions.length }} 题</span>
            <span class="q-score">本题 {{ current.score }} 分</span>
          </div>
          <div class="q-stem">{{ current.stem }}</div>
          <div class="q-options">
            <div
              v-for="opt in current.options"
              :key="opt.key"
              class="opt-item"
              :class="{ active: isSelected(opt.key) }"
              @click="choose(opt.key)"
            >
              <span class="opt-badge">{{ opt.key }}</span>
              <span class="opt-text">{{ opt.text }}</span>
            </div>
          </div>
        </template>
        <el-empty v-else-if="!loading" description="题目加载失败" />
      </div>
      <div class="exam-side">
        <div class="card-title">答题卡</div>
        <div class="card-grid">
          <div
            v-for="(q, i) in questions"
            :key="q.questionId"
            class="card-item"
            :class="{ active: i === index, done: isAnswered(q) }"
            @click="jump(i)"
          >
            {{ q.seq }}
          </div>
        </div>
        <div class="card-legend">
          <span><i class="dot dot-done" />已答</span>
          <span><i class="dot dot-current" />当前</span>
          <span><i class="dot dot-blank" />未答</span>
        </div>
        <div class="card-nav">
          <el-button :disabled="index <= 0" @click="prev">上一题</el-button>
          <el-button type="primary" :disabled="index >= questions.length - 1" @click="next">
            下一题
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExamQuestions } from '../api/exams'
import { submitAnswers } from '../api/scores'
import { getLoginUser } from '../stores/auth'

const route = useRoute()
const router = useRouter()

const paperId = Number(route.params.paperId)
const loading = ref(true)
const submitting = ref(false)

const paper = ref({
  title: '',
  durationSec: 0,
  totalScore: 0,
  questionCount: 0
})
const questions = ref([])
const index = ref(0)
// answers: { [questionId]: key 或 key 数组（多选） }
const answers = ref({})
const remaining = ref(0)

let timer = null

const current = computed(() => questions.value[index.value] || null)
const answeredCount = computed(() => questions.value.filter((q) => isAnswered(q)).length)

function isAnswered(q) {
  const v = answers.value[q.questionId]
  if (q.type === 'multi') {
    return Array.isArray(v) && v.length > 0
  }
  return v !== undefined && v !== ''
}

function isSelected(key) {
  const q = current.value
  if (!q) return false
  const v = answers.value[q.questionId]
  if (q.type === 'multi') {
    return Array.isArray(v) && v.includes(key)
  }
  return v === key
}

function choose(key) {
  const q = current.value
  if (!q) return
  if (q.type === 'multi') {
    const list = Array.isArray(answers.value[q.questionId]) ? [...answers.value[q.questionId]] : []
    const pos = list.indexOf(key)
    if (pos >= 0) {
      list.splice(pos, 1)
    } else {
      list.push(key)
    }
    answers.value[q.questionId] = list
  } else {
    answers.value[q.questionId] = key
    if (index.value < questions.value.length - 1) {
      index.value += 1
    }
  }
}

function prev() {
  if (index.value > 0) {
    index.value -= 1
  }
}

function next() {
  if (index.value < questions.value.length - 1) {
    index.value += 1
  }
}

function jump(i) {
  index.value = i
}

function formatTime(totalSec) {
  const h = Math.floor(totalSec / 3600)
  const m = Math.floor((totalSec % 3600) / 60)
  const s = totalSec % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h > 0 ? `${String(h).padStart(2, '0')}:${mm}:${ss}` : `${mm}:${ss}`
}

function startTimer() {
  timer = setInterval(() => {
    remaining.value -= 1
    if (remaining.value <= 0) {
      remaining.value = 0
      stopTimer()
      ElMessage.warning('考试时间到，系统自动交卷')
      doSubmit(true)
    }
  }, 1000)
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function onKeyDown(e) {
  if (submitting.value) return
  const key = e.key
  if (key === 'ArrowLeft') {
    e.preventDefault()
    prev()
    return
  }
  if (key === 'ArrowRight' || key === 'Enter') {
    e.preventDefault()
    if (key === 'Enter' && index.value === questions.value.length - 1) {
      onSubmitClick()
      return
    }
    next()
    return
  }
  const q = current.value
  if (!q) return
  const upper = key.toUpperCase()
  const keyIndex = 'ABCDE'.indexOf(upper)
  const numIndex = '12345'.indexOf(key)
  const optIndex = keyIndex >= 0 ? keyIndex : numIndex
  if (optIndex >= 0 && optIndex < q.options.length) {
    choose(q.options[optIndex].key)
  }
}

function onSubmitClick() {
  const blank = questions.value.length - answeredCount.value
  const tip =
    blank > 0 ? `还有 ${blank} 题未作答，确定要交卷吗？` : '全部作答完毕，确定要交卷吗？'
  ElMessageBox.confirm(tip, '交卷确认', {
    confirmButtonText: '确定交卷',
    cancelButtonText: '继续答题',
    type: 'warning'
  })
    .then(() => {
      doSubmit(false)
    })
    .catch(() => {})
}

async function doSubmit(auto) {
  if (submitting.value) return
  submitting.value = true
  stopTimer()
  try {
    const payload = {
      paperId,
      answers: questions.value
        .filter((q) => isAnswered(q))
        .map((q) => ({ questionId: q.questionId, chosen: answers.value[q.questionId] }))
    }
    await submitAnswers(payload)
    ElMessage.success(auto ? '考试时间到，已自动交卷' : '交卷成功')
    goScoreDetail()
  } catch (e) {
    // 提交失败（网络/重复交卷 409 等）恢复计时器，让考生能继续操作或看到提示
    submitting.value = false
    if (remaining.value > 0) {
      startTimer()
    }
  }
}

function goScoreDetail() {
  // 跳到「我的成绩」并带上 paperId/userId，那边会自动打开明细抽屉
  const user = getLoginUser()
  router.replace({
    path: '/my-scores',
    query: { paperId: String(paperId), userId: user ? String(user.id) : '' }
  })
}

onMounted(async () => {
  try {
    const data = await getExamQuestions(paperId)
    paper.value = data
    questions.value = data.questions || []
    remaining.value = data.durationSec || 0
    startTimer()
    window.addEventListener('keydown', onKeyDown)
  } catch (e) {
    // 409（已交卷/未发布）等错误已弹提示，回考试中心
    router.replace('/exam-center')
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  stopTimer()
  window.removeEventListener('keydown', onKeyDown)
})
</script>

<style scoped>
.exam-room {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow: hidden;
}

.exam-header {
  height: 56px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.exam-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.exam-header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.exam-timer {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  font-variant-numeric: tabular-nums;
}

.exam-timer.danger {
  color: #f56c6c;
}

.exam-progress {
  color: #606266;
  font-size: 14px;
}

.exam-body {
  flex: 1;
  display: flex;
  min-height: 0;
  padding: 16px 20px;
  gap: 16px;
}

.exam-main {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  padding: 24px;
  overflow-y: auto;
}

.q-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.q-seq {
  color: #303133;
  font-size: 14px;
}

.q-score {
  color: #909399;
  font-size: 13px;
}

.q-stem {
  font-size: 16px;
  color: #303133;
  line-height: 1.8;
  margin-bottom: 24px;
  white-space: pre-wrap;
}

.q-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.opt-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.opt-item:hover {
  border-color: #409eff;
}

.opt-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.opt-badge {
  width: 26px;
  height: 26px;
  line-height: 26px;
  text-align: center;
  border: 1px solid #dcdfe6;
  border-radius: 50%;
  font-size: 13px;
  color: #606266;
  flex-shrink: 0;
}

.opt-item.active .opt-badge {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.opt-text {
  color: #303133;
  font-size: 14px;
  line-height: 1.6;
}

.exam-side {
  width: 280px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.card-grid {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  align-content: start;
}

.card-item {
  height: 32px;
  line-height: 32px;
  text-align: center;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
}

.card-item.done {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.card-item.active {
  border-color: #409eff;
  color: #409eff;
  font-weight: 600;
}

.card-item.done.active {
  background: #ecf5ff;
}

.card-legend {
  display: flex;
  gap: 14px;
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
}

.card-legend .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 4px;
}

.dot-done {
  background: #409eff;
}

.dot-current {
  background: #fff;
  border: 1px solid #409eff;
}

.dot-blank {
  background: #fff;
  border: 1px solid #dcdfe6;
}

.card-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}

.card-nav .el-button + .el-button {
  margin-left: 0;
}
</style>
