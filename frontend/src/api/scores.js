import request from './request'

export function submitAnswers(data) {
  // data: {paperId, answers: [{questionId, chosen}]}
  return request.post('/answers/submit', data)
}

export function listScores(params) {
  return request.get('/scores', { params })
}

export function getScoreDetail(paperId, userId) {
  return request.get(`/scores/${paperId}/${userId}`)
}

export function deleteScore(paperId, userId) {
  return request.delete(`/scores/${paperId}/${userId}`)
}

export function getStats() {
  return request.get('/scores/stats')
}

export function getRanking(params) {
  // params: {paperId, limit}
  return request.get('/scores/ranking', { params })
}
