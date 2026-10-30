import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, clearLoginInfo } from '../stores/auth'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

function toLogin() {
  clearLoginInfo()
  if (window.location.pathname !== '/login') {
    const redirect = encodeURIComponent(window.location.pathname + window.location.search)
    window.location.href = `/login?redirect=${redirect}`
  }
}

request.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) {
        return body.data
      }
      if (body.code === 401) {
        clearLoginInfo()
        toLogin()
      }
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return body
  },
  (error) => {
    const body = error.response && error.response.data
    const message = (body && body.message) || error.message || '网络异常，请稍后重试'
    if (error.response && error.response.status === 401) {
      ElMessage.error(message)
      toLogin()
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(new Error(message))
  }
)

export default request
