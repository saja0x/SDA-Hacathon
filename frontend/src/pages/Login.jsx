import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  // Controlled inputs: React state is the source of truth for the
  // form, not the DOM.
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    // Stop the browser from doing a full-page form POST -- we're
    // handling the submit with fetch instead.
    e.preventDefault()
    setError('')

    try {
      await login(email, password)
      navigate('/contract')
    } catch (err) {
      // The message comes from the backend's "detail" field, e.g.
      // "Incorrect email or password".
      setError(err.message)
    }
  }

  return (
    <div className="card">
      <h1>تسجيل الدخول</h1>
      {error && <p className="error" style={{ background: '#FEF2F2', color: '#DC2626', padding: '10px', borderRadius: '8px' }}>{error === 'Incorrect email or password' ? 'البريد الإلكتروني أو كلمة المرور غير صحيحة' : error}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          البريد الإلكتروني
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="example@mail.com"
          />
        </label>
        <label>
          الرقم السري
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••"
          />
        </label>
        <button type="submit">دخول</button>
      </form>
      <p>
        ليس لديك حساب؟ <Link to="/register">إنشاء حساب جديد</Link>
      </p>
    </div>
  )
}
