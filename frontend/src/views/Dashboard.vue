<template>
  <div class="page">
    <el-row :gutter="16">
      <el-col :span="6" v-for="c in topCards" :key="c.key">
        <el-card class="stat-card">
          <div class="stat-value">{{ c.value }}</div>
          <div class="stat-label">{{ c.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" class="mt16">
      <el-col :span="12">
        <el-card>
          <template #header>按题型分布</template>
          <el-table :data="stats.byType" border>
            <el-table-column prop="typeText" label="题型" />
            <el-table-column prop="count" label="题目数" width="120" />
            <el-table-column label="占比">
              <template #default="{ row }">
                <el-progress :percentage="typePercent(row.count)" :stroke-width="14" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>按题库分布</template>
          <el-table :data="stats.byBank" border>
            <el-table-column prop="bankName" label="题库" />
            <el-table-column prop="questionCount" label="题目数" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import { getStats } from '../api/scores'

const stats = reactive({
  bankCount: 0,
  questionCount: 0,
  paperCount: 0,
  userCount: 0,
  submittedCount: 0,
  avgScore: 0,
  passRate: 0,
  byType: [],
  byBank: []
})

const topCards = computed(() => [
  { key: 'bankCount', label: '题库数', value: stats.bankCount },
  { key: 'questionCount', label: '题目总数', value: stats.questionCount },
  { key: 'paperCount', label: '试卷数', value: stats.paperCount },
  { key: 'userCount', label: '考生数', value: stats.userCount },
  { key: 'submittedCount', label: '已交卷次数', value: stats.submittedCount },
  { key: 'avgScore', label: '平均分', value: stats.avgScore },
  { key: 'passRate', label: '通过率', value: stats.passRate }
])

const typeTotal = computed(() => stats.byType.reduce((sum, t) => sum + (t.count || 0), 0))

function typePercent(count) {
  if (!typeTotal.value) return 0
  return Math.round((count / typeTotal.value) * 100)
}

onMounted(async () => {
  const data = await getStats()
  Object.assign(stats, data)
})
</script>

<style scoped>
.mt16 {
  margin-top: 16px;
}
</style>
