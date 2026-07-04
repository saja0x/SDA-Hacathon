import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  // The role dropdown exists so the class can create both kinds of
  // account and see RBAC in action. In a real app the server would
  // assign roles -- letting users pick "admin" defeats the purpose.
  const [role, setRole] = useState('user')
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    try {
      // register() also logs in afterwards (see AuthContext), so we
      // can go straight to the dashboard.
      await register(email, password, role)
      navigate('/contract')
    } catch (err) {
      if (err.message.includes("422") || err.message.includes("Unprocessable Entity") || err.message.includes("validation")) {
        setError('الرقم السري يجب أن يكون 6 أحرف على الأقل، أو البريد الإلكتروني غير صحيح.')
      } else {
        setError(err.message)
      }
    }
  }

  return (
    <div className="card">
      <h1>إنشاء حساب جديد</h1>
      {error && <p className="error" style={{ background: '#FEF2F2', color: '#DC2626', padding: '10px', borderRadius: '8px' }}>{error}</p>}
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
          الرقم السري (6 أحرف على الأقل)
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={6}
            required
            placeholder="••••••"
          />
        </label>
        <label>
          نوع الحساب
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="user">مستخدم عادي</option>
            <option value="admin">محامي (استشاري)</option>
          </select>
        </label>
        <button type="submit">تسجيل</button>
      </form>
      <p>
        لديك حساب بالفعل؟ <Link to="/login">تسجيل الدخول</Link>
      </p>
    </div>
  )
}
