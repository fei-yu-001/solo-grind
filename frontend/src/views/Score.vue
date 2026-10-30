<template>
  <div class="page">
    <el-card>
      <div class="filter-bar">
        <el-select v-model="query.paperId" placeholder="试卷" clearable filterable style="width: 240px">
          <el-option v-for="p in papers" :key="p.id" :label="p.title" :value="p.id" />
        </el-select>
        <el-input
          v-model="query.keyword"
          placeholder="考生名/账号"
          clearable
          style="width: 180px"
          @keyup.enter="onSearch"
        />
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button type="warning" plain class="rank-btn" @click="openRanking">排行榜</el-button>
      </div>
      <el-table v-loading="loading" :data="records" border>
        <el-table-column label="考生" min-width="130">
          <template #default="{ row }">
            {{ row.nickname }}（{{ row.username }}）
          </template>
        </el-table-column>
        <el-table-column prop="paperTitle" label="试卷" min-width="200" show-overflow-tooltip />
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
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="onDetail(row)">看明细</el-button>
            <el-button type="danger" link @click="onRevoke(row)">撤销成绩</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="pager"
        layout="total, prev, pager, next, sizes"
        :total="total"
        :current-page="query.page"
        :page-size="query.size"
        :page-sizes="[10, 20, 50]"
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </el-card>

    <el-drawer v-model="detailVisible" title="作答明细" size="55%">
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border class="detail-head">
          <el-descriptions-item label="考生">{{ detailHead.nickname }}</el-descriptions-item>
          <el-descriptions-item label="试卷">{{ detailHead.paperTitle }}</el-descriptions-item>
          <el-descriptions-item label="得分">
            {{ detailHead.totalScore }} / {{ detailHead.maxScore }}
          </el-descriptions-item>
          <el-descriptions-item label="交卷时间">{{ detailHead.submittedAt }}</el-descriptions-item>
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

    <el-dialog v-model="rankVisible" title="排行榜" width="480px">
      <div v-if="rankPaperTitle" class="rank-paper">试卷：{{ rankPaperTitle }}</div>
      <div v-loading="rankLoading">
        <el-empty v-if="!rankLoading && ranking.length === 0" description="暂无成绩" />
        <el-table v-else :data="ranking" border>
          <el-table-column prop="rank" label="名次" width="70" />
          <el-table-column prop="nickname" label="考生" />
          <el-table-column prop="totalScore" label="得分" width="90" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listScores, getScoreDetail, deleteScore, getRanking } from '../api/scores'
import { listPapers } from '../api/papers'

const loading = ref(false)
const records = ref([])
const total = ref(0)
const papers = ref([])

const query = reactive({
  paperId: null,
  keyword: '',
  page: 1,
  size: 10
})

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailHead = reactive({
  nickname: '',
  paperTitle: '',
  totalScore: '',
  maxScore: '',
  submittedAt: ''
})
const items = ref([])

const rankVisible = ref(false)
const rankLoading = ref(false)
const ranking = ref([])
const rankPaperTitle = ref('')

function cleanParams(q) {
  const p = {}
  Object.keys(q).forEach((k) => {
    const v = q[k]
    if (v !== '' && v !== null && v !== undefined) {
      p[k] = v
    }
  })
  return p
}

function loadData() {
  loading.value = listScores(cleanParams(query))
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

function onSearch() {
  query.page = 1
  loadData()
}

function onPageChange(page) {
  query.page = page
  loadData()
}

function onSizeChange(size) {
  query.size = size
  query.page = 1
  loadData()
}

function onDetail(row) {
  detailVisible.value = true
  detailLoading.value = true
  items.value = []
  Object.assign(detailHead, {
    nickname: `${row.nickname}（${row.username}）`,
    paperTitle: row.paperTitle,
    totalScore: row.totalScore,
    maxScore: row.maxScore,
    submittedAt: row.submittedAt
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

function onRevoke(row) {
  ElMessageBox.confirm(
    `确定撤销 ${row.nickname} 在「${row.paperTitle}」的成绩吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      await deleteScore(row.paperId, row.userId)
      ElMessage.success('已撤销')
      loadData()
    })
    .catch(() => {})
}

function openRanking() {
  rankVisible.value = true
  rankLoading.value = true
  ranking.value = []
  const paper = papers.value.find((p) => p.id === query.paperId)
  rankPaperTitle.value = paper ? paper.title : ''
  const params = { limit: 10 }
  if (query.paperId) {
    params.paperId = query.paperId
  }
  getRanking(params)
    .then((list) => {
      ranking.value = list || []
    })
    .catch(() => {})
    .finally(() => {
      rankLoading.value = false
    })
}

onMounted(() => {
  loadData()
  listPapers({ page: 1, size: 100 })
    .then((data) => {
      papers.value = data.records || []
    })
    .catch(() => {})
})
</script>

<style scoped>
.rank-btn {
  margin-left: auto;
}

.rank-paper {
  margin-bottom: 12px;
  color: #606266;
}

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
