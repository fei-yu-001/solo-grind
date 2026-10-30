<template>
  <div class="page">
    <el-card>
      <div class="filter-bar">
        <el-input
          v-model="query.keyword"
          placeholder="试卷名关键字"
          clearable
          style="width: 200px"
          @keyup.enter="onSearch"
        />
        <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
          <el-option label="草稿" value="DRAFT" />
          <el-option label="已发布" value="PUBLISHED" />
          <el-option label="已结束" value="CLOSED" />
        </el-select>
        <el-select v-model="query.bankId" placeholder="题库" clearable style="width: 220px">
          <el-option v-for="b in banks" :key="b.id" :label="b.name" :value="b.id" />
        </el-select>
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button type="primary" plain @click="openCompose">组卷</el-button>
      </div>
      <el-table v-loading="loading" :data="records" border>
        <el-table-column prop="title" label="试卷名" min-width="220" show-overflow-tooltip />
        <el-table-column prop="bankName" label="来源题库" min-width="160" show-overflow-tooltip />
        <el-table-column label="题量（判断/单选/多选）" width="180">
          <template #default="{ row }">
            {{ row.judgeCount }} / {{ row.singleCount }} / {{ row.multiCount }}
          </template>
        </el-table-column>
        <el-table-column prop="totalScore" label="总分" width="80" />
        <el-table-column label="时长（分钟）" width="110">
          <template #default="{ row }">
            {{ Math.round(row.durationSec / 60) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="onView(row)">查看题目</el-button>
            <el-button v-if="row.status === 'DRAFT'" type="primary" link @click="onEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'DRAFT'" type="success" link @click="onPublish(row)">发布</el-button>
            <el-button v-if="row.status === 'PUBLISHED'" type="warning" link @click="onClose(row)">结束</el-button>
            <el-button type="danger" link @click="onDelete(row)">删除</el-button>
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

    <PaperFormDialog v-model="composeVisible" :banks="banks" @saved="loadData" />

    <el-dialog v-model="editVisible" title="编辑试卷" width="560px" @closed="resetEditForm">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="120px">
        <el-form-item label="试卷标题" prop="title">
          <el-input v-model="editForm.title" maxlength="150" />
        </el-form-item>
        <el-form-item label="考试时长（分钟）" prop="durationMin">
          <el-input-number v-model="editForm.durationMin" :min="1" :max="600" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSubmitting" @click="onEditSave">保存</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailVisible" title="试卷题目" size="55%">
      <div v-loading="detailLoading">
        <el-empty v-if="!detailLoading && detailQuestions.length === 0" description="暂无题目" />
        <el-collapse v-else>
          <el-collapse-item v-for="q in detailQuestions" :key="q.id" :name="q.id">
            <template #title>
              <span class="dq-title">{{ q.seq }}. [{{ q.typeText }}] {{ q.stem }}</span>
            </template>
            <div v-if="q.options && q.options.length" class="dq-options">
              <div v-for="opt in q.options" :key="opt.key">{{ opt.key }}. {{ opt.text }}</div>
            </div>
            <div class="dq-answer">
              <el-tag type="success">答案：{{ formatAnswer(q) }}</el-tag>
              <el-tag v-if="q.analysis" type="info" class="dq-analysis">解析：{{ q.analysis }}</el-tag>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listPapers,
  getPaper,
  updatePaper,
  deletePaper,
  publishPaper,
  closePaper
} from '../api/papers'
import { listAllBanks } from '../api/banks'
import PaperFormDialog from '../components/PaperFormDialog.vue'

const loading = ref(false)
const records = ref([])
const total = ref(0)
const banks = ref([])

const query = reactive({
  keyword: '',
  status: '',
  bankId: null,
  page: 1,
  size: 10
})

const composeVisible = ref(false)

const editVisible = ref(false)
const editSubmitting = ref(false)
const editFormRef = ref()
const editingPaper = ref(null)
const editForm = reactive({
  id: null,
  title: '',
  durationMin: 100
})
const editRules = {
  title: [{ required: true, message: '请输入试卷标题', trigger: 'blur' }]
}

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailQuestions = ref([])

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
  loading.value = true
  listPapers(cleanParams(query))
    .then((data) => {
      records.value = data.records || []
      total.value = data.total || 0
    })
    .finally(() => {
      loading.value = false
    })
}

function statusTag(status) {
  if (status === 'PUBLISHED') return 'success'
  if (status === 'CLOSED') return 'info'
  return 'warning'
}

function formatAnswer(q) {
  return Array.isArray(q.answer) ? q.answer.join('、') : q.answer
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

function openCompose() {
  composeVisible.value = true
}

function onView(row) {
  detailVisible.value = true
  detailLoading.value = true
  detailQuestions.value = []
  getPaper(row.id)
    .then((data) => {
      detailQuestions.value = data.questions || []
    })
    .catch(() => {})
    .finally(() => {
      detailLoading.value = false
    })
}

function onEdit(row) {
  editingPaper.value = row
  editForm.id = row.id
  editForm.title = row.title
  editForm.durationMin = Math.round(row.durationSec / 60)
  editVisible.value = true
}

function resetEditForm() {
  editFormRef.value && editFormRef.value.clearValidate()
}

async function onEditSave() {
  try {
    await editFormRef.value.validate()
  } catch (e) {
    return
  }
  editSubmitting.value = true
  try {
    const paper = editingPaper.value
    await updatePaper(paper.id, {
      title: editForm.title.trim(),
      bankId: paper.bankId,
      judgeCount: paper.judgeCount,
      singleCount: paper.singleCount,
      multiCount: paper.multiCount,
      judgeScore: paper.judgeScore,
      singleScore: paper.singleScore,
      multiScore: paper.multiScore,
      durationSec: editForm.durationMin * 60
    })
    ElMessage.success('保存成功')
    editVisible.value = false
    loadData()
  } catch (e) {
    // 错误提示已由 request 拦截器统一弹出
  } finally {
    editSubmitting.value = false
  }
}

function onPublish(row) {
  ElMessageBox.confirm(`确定发布试卷「${row.title}」吗？发布后不可编辑。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await publishPaper(row.id)
      ElMessage.success('发布成功')
      loadData()
    })
    .catch(() => {})
}

function onClose(row) {
  ElMessageBox.confirm(`确定结束试卷「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await closePaper(row.id)
      ElMessage.success('已结束')
      loadData()
    })
    .catch(() => {})
}

function onDelete(row) {
  ElMessageBox.confirm(`确定删除试卷「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await deletePaper(row.id)
      ElMessage.success('删除成功')
      loadData()
    })
    .catch(() => {})
}

onMounted(() => {
  loadData()
  listAllBanks()
    .then((list) => {
      banks.value = list || []
    })
    .catch(() => {})
})
</script>

<style scoped>
.dq-title {
  font-size: 14px;
}

.dq-options {
  color: #606266;
  line-height: 1.8;
}

.dq-answer {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dq-analysis {
  max-width: 100%;
}
</style>
