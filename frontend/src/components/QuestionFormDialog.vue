<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑题目' : '新增题目'"
    width="720px"
    @update:model-value="$emit('update:modelValue', $event)"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="所属题库" prop="bankId">
        <el-select v-model="form.bankId" placeholder="请选择题库" style="width: 100%">
          <el-option v-for="b in banks" :key="b.id" :label="b.name" :value="b.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="题型" prop="type">
        <el-radio-group v-model="form.type" @change="onTypeChange">
          <el-radio value="single">单选题</el-radio>
          <el-radio value="multi">多选题</el-radio>
          <el-radio value="judge">判断题</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="题干" prop="stem">
        <el-input v-model="form.stem" type="textarea" :rows="4" maxlength="1000" />
      </el-form-item>
      <el-form-item
        v-for="(opt, idx) in form.options"
        :key="idx"
        :label="idx === 0 ? '选项' : ''"
        :prop="'options.' + idx + '.text'"
        :rules="{ required: form.type !== 'judge', message: '请输入选项内容', trigger: 'blur' }"
      >
        <div class="opt-row">
          <el-tag class="opt-key">{{ opt.key }}</el-tag>
          <el-input v-model="opt.text" :placeholder="'选项 ' + opt.key" />
          <el-button
            v-if="form.type === 'multi'"
            type="danger"
            link
            :disabled="form.options.length <= 4"
            @click="removeOption(idx)"
          >
            删除
          </el-button>
        </div>
      </el-form-item>
      <el-form-item v-if="form.type === 'multi'" label="">
        <el-button type="primary" plain :disabled="form.options.length >= 6" @click="addOption">
          添加选项
        </el-button>
      </el-form-item>
      <el-form-item label="正确答案" prop="answer">
        <el-radio-group v-if="form.type === 'single'" v-model="form.answer">
          <el-radio v-for="opt in form.options" :key="opt.key" :value="opt.key">{{ opt.key }}</el-radio>
        </el-radio-group>
        <el-checkbox-group v-else-if="form.type === 'multi'" v-model="form.answer">
          <el-checkbox v-for="opt in form.options" :key="opt.key" :value="opt.key">{{ opt.key }}</el-checkbox>
        </el-checkbox-group>
        <el-radio-group v-else-if="form.type === 'judge'" v-model="form.answer">
          <el-radio-button value="A">对</el-radio-button>
          <el-radio-button value="B">错</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="解析">
        <el-input v-model="form.analysis" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item label="难度" prop="difficulty">
        <el-radio-group v-model="form.difficulty">
          <el-radio :value="1">易</el-radio>
          <el-radio :value="2">中</el-radio>
          <el-radio :value="3">难</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="排序号" prop="sortNo">
        <el-input-number v-model="form.sortNo" :min="1" />
      </el-form-item>
      <el-form-item label="标签">
        <el-select v-model="form.tagIds" multiple placeholder="可选多个标签" style="width: 100%">
          <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createQuestion, updateQuestion } from '../api/questions'

const props = defineProps({
  modelValue: Boolean,
  question: Object,
  banks: { type: Array, default: () => [] },
  tags: { type: Array, default: () => [] }
})
const emit = defineEmits(['update:modelValue', 'saved'])

const KEYS6 = ['A', 'B', 'C', 'D', 'E', 'F']

const formRef = ref()
const submitting = ref(false)
const isEdit = computed(() => !!props.question)

const form = reactive({
  bankId: null,
  type: 'single',
  stem: '',
  options: [],
  answer: '',
  analysis: '',
  difficulty: 1,
  sortNo: 1,
  tagIds: []
})

const rules = {
  bankId: [{ required: true, message: '请选择题库', trigger: 'change' }],
  type: [{ required: true, message: '请选择题型', trigger: 'change' }],
  stem: [{ required: true, message: '请输入题干', trigger: 'blur' }],
  answer: [{ required: true, validator: validateAnswer, trigger: 'change' }]
}

function validateAnswer(rule, value, callback) {
  if (form.type === 'multi') {
    if (!Array.isArray(form.answer) || form.answer.length === 0) {
      return callback(new Error('请至少勾选一个正确答案'))
    }
  } else if (!form.answer) {
    return callback(new Error('请设置正确答案'))
  }
  callback()
}

function buildOptions(type, existing) {
  const old = existing || []
  if (type === 'judge') {
    if (old.length === 2) {
      return [{ key: 'A', text: old[0].text || '对' }, { key: 'B', text: old[1].text || '错' }]
    }
    return [{ key: 'A', text: '对' }, { key: 'B', text: '错' }]
  }
  if (type === 'single') {
    return KEYS6.slice(0, 4).map((k, i) => ({
      key: k,
      text: old[i] && old[i].key === k ? old[i].text : ''
    }))
  }
  // multi: 保留已有选项，不足 4 个补空
  const base = old.map((o) => ({ key: o.key, text: o.text }))
  while (base.length < 4) {
    base.push({ key: KEYS6[base.length], text: '' })
  }
  base.forEach((o, i) => {
    o.key = KEYS6[i]
  })
  return base.slice(0, 6)
}

function onTypeChange(type) {
  form.options = buildOptions(type, form.options)
  form.answer = type === 'multi' ? [] : ''
}

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    if (props.question) {
      const q = props.question
      form.bankId = q.bankId
      form.type = q.type
      form.stem = q.stem || ''
      form.options = buildOptions(q.type, q.options)
      form.answer = Array.isArray(q.answer) ? [...q.answer] : q.answer || ''
      form.analysis = q.analysis || ''
      form.difficulty = q.difficulty || 1
      form.sortNo = q.sortNo || 1
      form.tagIds = (q.tags || []).map((t) => t.id)
    } else {
      form.bankId = null
      form.type = 'single'
      form.stem = ''
      form.options = buildOptions('single', [])
      form.answer = ''
      form.analysis = ''
      form.difficulty = 1
      form.sortNo = 1
      form.tagIds = []
    }
    formRef.value && formRef.value.clearValidate()
  }
)

function resetForm() {
  formRef.value && formRef.value.clearValidate()
}

function addOption() {
  if (form.options.length >= 6) return
  form.options.push({ key: KEYS6[form.options.length], text: '' })
}

function removeOption(idx) {
  if (form.options.length <= 4) return
  form.options.splice(idx, 1)
  form.options.forEach((o, i) => {
    o.key = KEYS6[i]
  })
  if (Array.isArray(form.answer)) {
    const keys = form.options.map((o) => o.key)
    form.answer = form.answer.filter((k) => keys.includes(k))
  }
}

function buildPayload() {
  return {
    bankId: form.bankId,
    type: form.type,
    stem: form.stem.trim(),
    options: form.options.map((o) => ({ key: o.key, text: o.text })),
    answer: form.type === 'multi' ? [...form.answer].sort() : form.answer,
    analysis: form.analysis || '',
    difficulty: form.difficulty,
    sortNo: form.sortNo,
    tagIds: form.tagIds
  }
}

async function onSubmit() {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  submitting.value = true
  try {
    if (props.question) {
      await updateQuestion(props.question.id, buildPayload())
    } else {
      await createQuestion(buildPayload())
    }
    ElMessage.success('保存成功')
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
.opt-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.opt-key {
  flex-shrink: 0;
}
</style>
