import request from './request'

export function listBanks(params) {
  return request.get('/banks', { params })
}

export function listAllBanks() {
  return request.get('/banks/all')
}

export function getBank(id) {
  return request.get(`/banks/${id}`)
}

export function createBank(data) {
  return request.post('/banks', data)
}

export function updateBank(id, data) {
  return request.put(`/banks/${id}`, data)
}

export function deleteBank(id) {
  return request.delete(`/banks/${id}`)
}
