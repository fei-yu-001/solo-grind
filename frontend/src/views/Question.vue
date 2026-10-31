<template>
  <div class="page">
    <el-card>
      <div class="filter-bar">
        <el-select v-model="query.bankId" placeholder="题库" clearable style="width: 220px">
          <el-option v-for="b in banks" :key="b.id" :label="b.name" :value="b.id" />
        </el-select>
        <el-select v-model="query.type" placeholder="题型" clearable style="width: 130px">
          <el-option label="单选题" value="single" />
          <el-option label="多选题" value="multi" />
          <el-option label="判断题" value="judge" />
        </el-select>
        <el-select v-model="query.difficulty" placeholder="难度" clearable style="width: 120px">
          <el-option label="易" :value="1" />
          <el-option label="中" :value="2" />
          <el-option label="难" :value="3" />
        </el-select>
        <el-select v-model="query.tagId" placeholder="标签" clearable style="width: 150px">
          <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
        <el-input
          v-model="query.keyword"
          placeholder="题干关键字"
          clearable
          style="width: 200px"
          @keyup.enter="onSearch"
        />
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button type="primary" plain @click="openDialog()">新增题目</el-button>
        <el-button type="warning" plain :disabled="!selection.length" @click="openBatchDialog">
          批量移动到题库
        </el-button>
        <el-button type="success" plain @click="importVisible = true">Word 导入</el-button>
      </div>
      <el-table v-loading="loading" :data="records" border @selection-change="onSelectionChange">
        <el-table-column type="selection" width="45" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="stem" label="题干" min-width="240" show-overflow-tooltip />
        <el-table-column label="题型" width="90">
          <template #default="{ row }">
            <el-tag>{{ row.typeText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="bankName" label="题库" min-width="150" show-overflow-tooltip />
        <el-table-column label="难度" width="80">
          <template #default="{ row }">
            <el-tag :type="difficultyTag(row.difficulty)" effect="plain">{{ row.difficultyText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="150">
          <template #default="{ row }">
            <el-tag
              v-for="t in row.tags"
              :key="t.id"
              size="small"
              effect="plain"
              class="q-tag"
            >
              {{ t.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDialog(row)">编辑</el-button>
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

    <QuestionFormDialog
      v-model="dialogVisible"
      :question="editingQuestion"
      :banks="banks"
      :tags="tags"
      @saved="loadData"
    />

    <QuestionImportDialog v-model="importVisible" :banks="banks" @imported="onImported" />

    <el-dialog v-model="batchVisible" title="批量移动到题库" width="420px">
      <el-select v-model="batchBankId" placeholder="请选择题库" style="width: 100%">
        <el-option v-for="b in banks" :key="b.id" :label="b.name" :value="b.id" />
      </el-select>
      <template #footer>
        <el-button @click="batchVisible = false">取消</el-button>
        <el-button type="primary" :loading="batchSubmitting" @click="onBatchMove">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listQuestions, deleteQuestion, batchMoveQuestions } from '../api/questions'
import { listAllBanks } from '../api/banks'
import { listTags } from '../api/tags'
import QuestionFormDialog from '../components/QuestionFormDialog.vue'
import QuestionImportDialog from '../components/QuestionImportDialog.vue'

const loading = ref(false)
const records = ref([])
const total = ref(0)
const banks = ref([])
const tags = ref([])
const selection = ref([])

const query = reactive({
  bankId: null,
  type: '',
  difficulty: null,
  tagId: null,
  keyword: '',
  page: 1,
  size: 10
})

const dialogVisible = ref(false)
const editingQuestion = ref(null)
const batchVisible = ref(false)
const batchBankId = ref(null)
const batchSubmitting = ref(false)
const importVisible = ref(false)

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
  listQuestions(cleanParams(query))
    .then((data) => {
      records.value = data.records || []
      total.value = data.total || 0
    })
    .finally(() => {
      loading.value = false
    })
}

function onSelectionChange(rows) {
  selection.value = rows
}

function difficultyTag(d) {
  if (d === 1) return 'success'
  if (d === 2) return 'warning'
  return 'danger'
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

function openDialog(row) {
  editingQuestion.value = row || null
  dialogVisible.value = true
}

function onDelete(row) {
  ElMessageBox.confirm('确定删除该题目吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await deleteQuestion(row.id)
      ElMessage.success('删除成功')
      loadData()
    })
    .catch(() => {})
}

function onImported() {
  query.page = 1
  loadData()
}

function openBatchDialog() {
  batchBankId.value = null
  batchVisible.value = true
}

async function onBatchMove() {
  if (!batchBankId.value) {
    ElMessage.warning('请选择题库')
    return
  }
  batchSubmitting.value = true
  try {
    const data = await batchMoveQuestions({
      ids: selection.value.map((row) => row.id),
      bankId: batchBankId.value
    })
    ElMessage.success(`已移动 ${data.updated} 道题`)
    batchVisible.value = false
    loadData()
  } catch (e) {
    // 错误提示已由 request 拦截器统一弹出
  } finally {
    batchSubmitting.value = false
  }
}

onMounted(() => {
  loadData()
  listAllBanks()
    .then((list) => {
      banks.value = list || []
    })
    .catch(() => {})
  listTags()
    .then((list) => {
      tags.value = list || []
    })
    .catch(() => {})
})
</script>

<style scoped>
.q-tag {
  margin-right: 6px;
}
</style>
