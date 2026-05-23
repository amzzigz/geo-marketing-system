import request from './index'

interface LoginData {
  username: string
  password: string
}

interface RegisterData {
  username: string
  password: string
  phone?: string
}

interface LoginResult {
  access_token: string
  token_type: string
}

interface UserInfo {
  id: number
  username: string
  role: string
}

/** 用户登录 */
export function loginApi(data: LoginData): Promise<LoginResult> {
  return request.post('/api/users/login', data)
}

/** 用户注册 */
export function registerApi(data: RegisterData): Promise<{ id: number; username: string }> {
  return request.post('/api/users/register', data)
}

/** 获取当前用户信息 */
export function getUserInfoApi(): Promise<UserInfo> {
  return request.get('/api/users/me')
}
