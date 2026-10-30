<template>
  <el-dialog
    :model-value="modelValue"
    title="组卷"
    width="560px"
    @update:model-value="$emit('update:modelValue', $event)"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="试卷标题" prop="title">
        <el-input v-model="form.title" maxlength="150" />
      </el-form-item>
      <el-form-item label="来源题库" prop="bankId">
        <el-select v-model="form.bankId" placeholder="请选择题库" style="width: 100%">
          <el-option v-for="b in banks" :key="b.id" :label="b.name" :value="b.id" />
        </el-select>
      </el-form-item>
      <el-divider content-position="left">题量与分值</el-divider>
      <el-form-item label="判断题">
        <el-input-number v-model="form.judgeCount" :min="0" :max="500" />
        <span class="num-label">题 x</span>
        <el-input-number v-model="form.judgeScore" :min="0" :max="100" />
        <span class="num-label">分</span>
      </el-form-item>
      <el-form-item label="单选题">
        <el-input-number v-model="form.singleCount" :min="0" :max="500" />
        <span class="num-label">题 x</span>
        <el-input-number v-model="form.singleScore" :min="0" :max="100" />
        <span class="num-label">分</span>
      </el-form-item>
      <el-form-item label="多选题">
        <el-input-number v-model="form.multiCount" :min="0" :max="500" />
        <span class="num-label">题 x</span>
        <el-input-number v-model="form.multiScore" :min="0" :max="100" />
        <span class="num-label">分</span>
      </el-form-item>
      <el-form-item label="考试时长（分钟）" prop="durationMin">
        <el-input-number v-model="form.durationMin" :min="1" :max="600" />
      </el-form-item>
      <el-form-item label="预览">
        <span>共 {{ totalQuestions }} 题，总分 {{ totalScore }} 分</span>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">生成试卷</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createPaper } from '../api/papers'

const props = defineProps({
  modelValue: Boolean,
  banks: { type: Array, default: () => [] }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const formRef = ref()
const submitting = ref(false)

const form = reactive({
  title: '',
  bankId: null,
  judgeCount: 0,
  judgeScore: 1,
  singleCount: 0,
  singleScore: 1,
  multiCount: 0,
  multiScore: 2,
  durationMin: 100
})

const rules = {
  title: [{ required: true, message: '请输入试卷标题', trigger: 'blur' }],
  bankId: [{ required: true, message: '请选择题库', trigger: 'change' }]
}

const totalQuestions = computed(() => form.judgeCount + form.singleCount + form.multiCount)

const totalScore = computed(
  () => form.judgeCount * form.judgeScore + form.singleCount * form.singleScore + form.multiCount * form.multiScore
)

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    form.title = ''
    form.bankId = null
    form.judgeCount = 0
    form.judgeScore = 1
    form.singleCount = 0
    form.singleScore = 1
    form.multiCount = 0
    form.multiScore = 2
    form.durationMin = 100
  }
)

function resetForm() {
  formRef.value && formRef.value.clearValidate()
}

async function onSubmit() {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  if (totalQuestions.value === 0) {
    ElMessage.warning('三种题型数量不能全为 0')
    return
  }
  submitting.value = true
  try {
    await createPaper({
      title: form.title.trim(),
      bankId: form.bankId,
      judgeCount: form.judgeCount,
      singleCount: form.singleCount,
      multiCount: form.multiCount,
      judgeScore: form.judgeScore,
      singleScore: form.singleScore,
      multiScore: form.multiScore,
      durationSec: form.durationMin * 60
    })
    ElMessage.success(`已生成 ${totalQuestions.value} 道题，总分 ${totalScore.value}`)
    emit('update:modelValue', false)
    emit('saved')
  } catch (e) {
    // 错误提示已由 request 拦截器统一弹出
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.num-label {
  margin: 0 12px 0 8px;
  color: #606266;
}
</style>
