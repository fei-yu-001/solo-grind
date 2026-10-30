import request from './request'

export function listBorrows(params) {
  return request.get('/borrows', { params })
}

export function createBorrow(data) {
  return request.post('/borrows', data)
}

export function returnBorrow(id) {
  return request.post(`/borrows/${id}/return`)
}

export function renewBorrow(id) {
  return request.post(`/borrows/${id}/renew`)
}

export function deleteBorrow(id) {
  return request.delete(`/borrows/${id}`)
}

export function getBorrowStats() {
  return request.get('/borrows/stats')
}
