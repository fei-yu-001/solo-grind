import request from './request'

export function listTags() {
  return request.get('/tags')
}

export function createTag(data) {
  // data: {name, color}
  return request.post('/tags', data)
}

export function deleteTag(id) {
  return request.delete(`/tags/${id}`)
}
