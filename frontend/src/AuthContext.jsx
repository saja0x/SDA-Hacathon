import { createContext, useContext, useEffect, useState } from 'react'
import { apiRequest } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { setUser(null); setLoading(false); return }
    apiRequest('/users/me', { token })
      .then(setUser)
      .catch(() => { localStorage.removeItem('token'); setToken(null) })
      .finally(() => setLoading(false))
  }, [token])

  async function login(email, password) {
    const data = await apiRequest('/auth/login', { method: 'POST', body: { email, password } })
    localStorage.setItem('token', data.access_token)
    setToken(data.access_token)
  }

  async function register(email, password, role) {
    await apiRequest('/auth/register', { method: 'POST', body: { email, password, role } })
    await login(email, password)
  }

  function logout() { localStorage.removeItem('token'); setToken(null) }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() { return useContext(AuthContext) }