import request from './request'

export function listReaders(params) {
  return request.get('/readers', { params })
}

export function getReader(id) {
  return request.get(`/readers/${id}`)
}

export function createReader(data) {
  return request.post('/readers', data)
}

export function updateReader(id, data) {
  return request.put(`/readers/${id}`, data)
}

export function deleteReader(id) {
  return request.delete(`/readers/${id}`)
}

export function updateReaderCard(id, data) {
  return request.patch(`/readers/${id}/card`, data)
}
