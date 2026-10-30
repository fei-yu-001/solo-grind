import request from './request'

export function getAvailableExams() {
  return request.get('/exams/available')
}

export function getExamQuestions(paperId) {
  return request.get(`/exams/${paperId}/questions`)
}
