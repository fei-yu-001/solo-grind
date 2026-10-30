const TOKEN_KEY = 'token'
const USERNAME_KEY = 'username'
const REALNAME_KEY = 'realName'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function isLoggedIn() {
  return !!getToken()
}

export function setLoginInfo({ token, username, realName }) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USERNAME_KEY, username)
  localStorage.setItem(REALNAME_KEY, realName)
}

export function getRealName() {
  return localStorage.getItem(REALNAME_KEY) || ''
}

export function clearLoginInfo() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)
  localStorage.removeItem(REALNAME_KEY)
}
