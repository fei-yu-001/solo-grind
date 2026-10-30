<template>
  <div class="page">
    <el-card>
      <div class="filter-bar">
        <el-input v-model="query.keyword" placeholder="题库名关键字" clearable @keyup.enter="onSearch" />
        <el-select v-model="query.groupName" placeholder="组别" clearable>
          <el-option v-for="g in groupOptions" :key="g" :label="g" :value="g" />
        </el-select>
        <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px">
          <el-option label="启用" value="ENABLED" />
          <el-option label="停用" value="DISABLED" />
        </el-select>
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button type="primary" plain @click="openDialog()">新增题库</el-button>
      </div>
      <el-table v-loading="loading" :data="records" border>
        <el-table-column prop="name" label="题库名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="groupName" label="组别" width="110" />
        <el-table-column prop="questionCount" label="题目数" width="90" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ENABLED' ? 'success' : 'info'">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="创建时间" width="170" />
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

    <BankFormDialog v-model="dialogVisible" :bank="editingBank" @saved="loadData" />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listBanks, listAllBanks, deleteBank } from '../api/banks'
import BankFormDialog from '../components/BankFormDialog.vue'

const loading = ref(false)
const records = ref([])
const total = ref(0)
const groupOptions = ref([])

const query = reactive({
  keyword: '',
  groupName: '',
  status: '',
  page: 1,
  size: 10
})

const dialogVisible = ref(false)
const editingBank = ref(null)

function loadData() {
  loading.value = true
  listBanks(query)
    .then((data) => {
      records.value = data.records || []
      total.value = data.total || 0
    })
    .finally(() => {
      loading.value = false
    })
}

function loadGroupOptions() {
  listAllBanks()
    .then((list) => {
      const groups = new Set((list || []).map((b) => b.groupName).filter(Boolean))
      groupOptions.value = Array.from(groups)
    })
    .catch(() => {})
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
  editingBank.value = row || null
  dialogVisible.value = true
}

function onDelete(row) {
  ElMessageBox.confirm(`确定删除题库「${row.name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      await deleteBank(row.id)
      ElMessage.success('删除成功')
      loadData()
    })
    .catch(() => {})
}

onMounted(() => {
  loadData()
  loadGroupOptions()
})
</script>
