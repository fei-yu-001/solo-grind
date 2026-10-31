import request from './request'

export function listQuestions(params) {
  return request.get('/questions', { params })
}

export function getQuestion(id) {
  return request.get(`/questions/${id}`)
}

export function createQuestion(data) {
  return request.post('/questions', data)
}

export function updateQuestion(id, data) {
  return request.put(`/questions/${id}`, data)
}

export function deleteQuestion(id) {
  return request.delete(`/questions/${id}`)
}

export function batchMoveQuestions(data) {
  // data: {ids: [], bankId}
  return request.patch('/questions/batch', data)
}

// Word 题库导入：file 为原始 File 对象
export function importQuestions(file, bankId, difficulty) {
  const form = new FormData()
  form.append('file', file)
  form.append('bankId', bankId)
  if (difficulty) {
    form.append('difficulty', difficulty)
  }
  return request.post('/questions/import', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
}
