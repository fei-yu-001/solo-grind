<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑题库' : '新增题库'"
    width="480px"
    @update:model-value="$emit('update:modelValue', $event)"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="题库名" prop="name">
        <el-input v-model="form.name" maxlength="100" />
      </el-form-item>
      <el-form-item label="组别" prop="groupName">
        <el-input v-model="form.groupName" maxlength="50" />
      </el-form-item>
      <el-form-item label="说明">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="状态">
        <el-radio-group v-model="form.status">
          <el-radio value="ENABLED">启用</el-radio>
          <el-radio value="DISABLED">停用</el-radio>
        </el-radio-group>
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
import { createBank, updateBank } from '../api/banks'

const props = defineProps({
  modelValue: Boolean,
  bank: Object
})
const emit = defineEmits(['update:modelValue', 'saved'])

const formRef = ref()
const submitting = ref(false)
const isEdit = computed(() => !!props.bank)

const form = reactive({
  name: '',
  groupName: '',
  description: '',
  status: 'ENABLED'
})

const rules = {
  name: [{ required: true, message: '请输入题库名', trigger: 'blur' }],
  groupName: [{ required: true, message: '请输入组别', trigger: 'blur' }]
}

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    if (props.bank) {
      form.name = props.bank.name || ''
      form.groupName = props.bank.groupName || ''
      form.description = props.bank.description || ''
      form.status = props.bank.status || 'ENABLED'
    } else {
      form.name = ''
      form.groupName = ''
      form.description = ''
      form.status = 'ENABLED'
    }
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
  submitting.value = true
  try {
    if (props.bank) {
      await updateBank(props.bank.id, { ...form })
    } else {
      await createBank({ ...form })
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
