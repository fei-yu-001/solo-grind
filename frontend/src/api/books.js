import request from './request'

export function listBooks(params) {
  return request.get('/books', { params })
}

export function getBook(id) {
  return request.get(`/books/${id}`)
}

export function createBook(data) {
  return request.post('/books', data)
}

export function updateBook(id, data) {
  return request.put(`/books/${id}`, data)
}

export function deleteBook(id) {
  return request.delete(`/books/${id}`)
}

export function updateBookStatus(data) {
  return request.patch('/books/status', data)
}

export function listAuthors() {
  return request.get('/authors')
}
