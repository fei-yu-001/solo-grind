<template>
  <el-dialog
    :model-value="modelValue"
    title="从 Word 导入题目"
    width="560px"
    @update:model-value="$emit('update:modelValue', $event)"
    @closed="reset"
  >
    <el-form label-width="90px">
      <el-form-item label="目标题库" required>
        <el-select v-model="bankId" placeholder="请选择题库" style="width: 100%">
          <el-option v-for="b in banks" :key="b.id" :label="b.name" :value="b.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="难度">
        <el-radio-group v-model="difficulty">
          <el-radio :value="1">易</el-radio>
          <el-radio :value="2">中</el-radio>
          <el-radio :value="3">难</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="Word 文件" required>
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".docx"
          :on-change="onFileChange"
          :on-exceed="onExceed"
          drag
          style="width: 100%"
        >
          <div class="upload-tip">把 .docx 拖到这里，或点击选择文件</div>
          <template #tip>
            <div class="upload-hint">
              题干行格式：<code>1-题目：题干[题型：单选题][答案：B]</code>
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">开始导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { importQuestions } from '../api/questions'

const props = defineProps({
  modelValue: Boolean,
  banks: { type: Array, default: () => [] }
})
const emit = defineEmits(['update:modelValue', 'imported'])

const uploadRef = ref()
const bankId = ref(null)
const difficulty = ref(1)
const file = ref(null)
const submitting = ref(false)

function onFileChange(uploadFile) {
  file.value = uploadFile.raw
}

function onExceed(files) {
  uploadRef.value.clearFiles()
  const raw = files[0]
  uploadRef.value.handleStart(raw)
  file.value = raw
}

function reset() {
  bankId.value = null
  difficulty.value = 1
  file.value = null
  uploadRef.value && uploadRef.value.clearFiles()
}

async function onSubmit() {
  if (!bankId.value) {
    ElMessage.warning('请选择目标题库')
    return
  }
  if (!file.value) {
    ElMessage.warning('请选择 .docx 文件')
    return
  }
  submitting.value = true
  try {
    const data = await importQuestions(file.value, bankId.value, difficulty.value)
    ElMessage.success(`导入成功，共 ${data.imported} 道题`)
    emit('update:modelValue', false)
    emit('imported')
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

.upload-hint {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(44, 44, 44, 0.55);
}

.upload-hint code {
  font-family: inherit;
  padding: 1px 4px;
  background: #ffd93d;
}
</style>
