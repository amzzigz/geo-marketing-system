import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, registerApi, getUserInfoApi } from '@/api/user'
import router from '@/router'

interface UserInfo {
  id: number
  username: string
  role: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  /** 登录 */
  async function login(username: string, password: string) {
    const data = await loginApi({ username, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
  }

  /** 注册 */
  async function register(username: string, password: string, phone?: string) {
    await registerApi({ username, password, phone })
  }

  /** 获取用户信息 */
  async function getUserInfo() {
    const data = await getUserInfoApi()
    userInfo.value = data
  }

  /** 退出登录 */
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, userInfo, login, register, getUserInfo, logout }
})
