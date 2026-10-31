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
      <el-form-item label="组别">
        <el-input v-model="form.groupName" maxlength="16" placeholder="可选，自定义，例如：本科组 / 第一章" />
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
      <el-form-item v-if="!isEdit" label="导入 Word">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".docx"
          :on-change="onFileChange"
          :on-remove="onFileRemove"
          :on-exceed="onExceed"
          drag
          style="width: 100%"
        >
          <div class="upload-tip">可选：拖入 .docx，保存时一起导入题目</div>
        </el-upload>
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
import { importQuestions } from '../api/questions'

const props = defineProps({
  modelValue: Boolean,
  bank: Object
})
const emit = defineEmits(['update:modelValue', 'saved'])

const formRef = ref()
const uploadRef = ref()
const file = ref(null)
const submitting = ref(false)
const isEdit = computed(() => !!props.bank)

const form = reactive({
  name: '',
  groupName: '',
  description: '',
  status: 'ENABLED'
})

const rules = {
  name: [{ required: true, message: '请输入题库名', trigger: 'blur' }]
}

function onFileChange(uploadFile) {
  file.value = uploadFile.raw
}

function onFileRemove() {
  file.value = null
}

function onExceed(files) {
  uploadRef.value.clearFiles()
  uploadRef.value.handleStart(files[0])
  file.value = files[0]
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
  file.value = null
  uploadRef.value && uploadRef.value.clearFiles()
}

async function onSubmit() {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  submitting.value = true
  try {
    const payload = { ...form, groupName: form.groupName.trim() || null }
    if (props.bank) {
      await updateBank(props.bank.id, payload)
      ElMessage.success('保存成功')
    } else {
      const bank = await createBank(payload)
      if (file.value) {
        try {
          const data = await importQuestions(file.value, bank.id, 1)
          ElMessage.success(`题库已创建，导入 ${data.imported} 道题`)
        } catch (e) {
          ElMessage.warning('题库已创建，但 Word 导入失败，可在题目页重新导入')
        }
      } else {
        ElMessage.success('保存成功')
      }
    }
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
.upload-tip {
  color: #2c2c2c;
  font-size: 14px;
}
</style>
