<template>
  <div class="page">
    <el-card>
      <el-table v-loading="loading" :data="records" border>
        <el-table-column prop="paperTitle" label="试卷" min-width="220" show-overflow-tooltip />
        <el-table-column label="得分/满分" width="100">
          <template #default="{ row }">
            {{ row.totalScore }} / {{ row.maxScore }}
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="90">
          <template #default="{ row }">
            {{ percent(row.accuracy) }}
          </template>
        </el-table-column>
        <el-table-column label="答对/答错/未答" width="140">
          <template #default="{ row }">
            {{ row.correctCount }} / {{ row.wrongCount }} / {{ row.blankCount }}
          </template>
        </el-table-column>
        <el-table-column prop="submittedAt" label="交卷时间" width="170" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="onDetail(row)">看明细</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="pager"
        layout="total, prev, pager, next"
        :total="total"
        :current-page="query.page"
        :page-size="query.size"
        @current-change="onPageChange"
      />
    </el-card>

    <el-drawer v-model="detailVisible" title="作答明细" size="55%">
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border class="detail-head">
          <el-descriptions-item label="试卷">{{ detailHead.paperTitle }}</el-descriptions-item>
          <el-descriptions-item label="得分">
            {{ detailHead.totalScore }} / {{ detailHead.maxScore }}
          </el-descriptions-item>
          <el-descriptions-item label="交卷时间">{{ detailHead.submittedAt }}</el-descriptions-item>
          <el-descriptions-item label="正确率">{{ detailHead.accuracy }}</el-descriptions-item>
        </el-descriptions>
        <el-empty v-if="!detailLoading && items.length === 0" description="暂无数据" />
        <el-collapse v-else>
          <el-collapse-item v-for="item in items" :key="item.questionId" :name="item.questionId">
            <template #title>
              <span class="item-title">
                {{ item.seq }}. [{{ item.typeText }}] {{ item.stem }}
                <el-tag :type="item.correct ? 'success' : 'danger'" size="small">
                  {{ item.correct ? '答对' : '答错' }}
                </el-tag>
              </span>
            </template>
            <div class="item-line">你的答案：{{ formatChosen(item.chosen) }}</div>
            <div class="item-line">正确答案：{{ formatChosen(item.answer) }}</div>
            <div class="item-line">得分：{{ item.score }}</div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getMyScores, getScoreDetail } from '../api/scores'

const route = useRoute()
const loading = ref(false)
const records = ref([])
const total = ref(0)

const query = reactive({
  page: 1,
  size: 10
})

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailHead = reactive({
  paperTitle: '',
  totalScore: '',
  maxScore: '',
  submittedAt: '',
  accuracy: ''
})
const items = ref([])

function loadData() {
  loading.value = true
  return getMyScores(query)
    .then((data) => {
      records.value = data.records || []
      total.value = data.total || 0
    })
    .finally(() => {
      loading.value = false
    })
}

function percent(acc) {
  if (acc === null || acc === undefined) return '-'
  return Math.round(acc * 100) + '%'
}

function formatChosen(v) {
  if (v === null || v === undefined || v === '') return '未作答'
  return Array.isArray(v) ? v.join('、') : v
}

function onPageChange(page) {
  query.page = page
  loadData()
}

function onDetail(row) {
  detailVisible.value = true
  detailLoading.value = true
  items.value = []
  Object.assign(detailHead, {
    paperTitle: row.paperTitle,
    totalScore: row.totalScore,
    maxScore: row.maxScore,
    submittedAt: row.submittedAt,
    accuracy: percent(row.accuracy)
  })
  getScoreDetail(row.paperId, row.userId)
    .then((data) => {
      items.value = data.items || []
    })
    .catch(() => {})
    .finally(() => {
      detailLoading.value = false
    })
}

onMounted(async () => {
  await loadData()
  // 从考试中心「查看成绩」跳过来时，直接打开对应试卷的明细
  if (route.query.paperId && route.query.userId) {
    const row = records.value.find(
      (r) => r.paperId === Number(route.query.paperId) && r.userId === Number(route.query.userId)
    )
    if (row) {
      onDetail(row)
    }
  }
})
</script>

<style scoped>
.detail-head {
  margin-bottom: 16px;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-line {
  line-height: 2;
  color: #606266;
}
</style>
