import request from './request'

export function listCategories(params) {
  return request.get('/categories', { params })
}

export function listAllCategories() {
  return request.get('/categories/all')
}

export function createCategory(data) {
  return request.post('/categories', data)
}

export function updateCategory(id, data) {
  return request.put(`/categories/${id}`, data)
}

export function deleteCategory(id) {
  return request.delete(`/categories/${id}`)
}
