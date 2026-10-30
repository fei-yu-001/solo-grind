import request from './request'

export function listPapers(params) {
  return request.get('/papers', { params })
}

export function getPaper(id) {
  return request.get(`/papers/${id}`)
}

export function createPaper(data) {
  return request.post('/papers', data)
}

export function updatePaper(id, data) {
  return request.put(`/papers/${id}`, data)
}

export function deletePaper(id) {
  return request.delete(`/papers/${id}`)
}

export function publishPaper(id) {
  return request.post(`/papers/${id}/publish`)
}

export function closePaper(id) {
  return request.post(`/papers/${id}/close`)
}
