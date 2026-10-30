const TOKEN_KEY = 'token'
const USER_KEY = 'loginUser'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function isLoggedIn() {
  return !!getToken()
}

export function setLoginInfo(data) {
  // data: {token, id, username, nickname, role}
  const { token, ...user } = data
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function getLoginUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch (e) {
    return null
  }
}

export function getRole() {
  const user = getLoginUser()
  return (user && user.role) || ''
}

export function isAdmin() {
  return getRole() === 'ADMIN'
}

export function clearLoginInfo() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}
