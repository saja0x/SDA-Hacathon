// The page every logged-in user can see. The user object was already
// loaded by AuthContext (via GET /users/me), so there's nothing to
// fetch here -- just display it.

import { useState } from 'react'
import { useAuth } from '../AuthContext'
import { useNavigate } from 'react-router-dom'
import { apiRequest } from '../api'

export default function Dashboard() {
  const { user, token } = useAuth()
  const navigate = useNavigate()

  const [isEditing, setIsEditing] = useState(false)
  const [fullName, setFullName] = useState(user.full_name || '')
  const [phone, setPhone] = useState(user.phone || '')
  const [saving, setSaving] = useState(false)
  const [localUser, setLocalUser] = useState(user)

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await apiRequest('/users/me', {
        method: 'PUT',
        token,
        body: { full_name: fullName, phone: phone }
      })
      setLocalUser(updated)
      setIsEditing(false)
    } catch (err) {
      alert('خطأ في حفظ البيانات: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-hero">
        <h1>أهلاً </h1>
        <p>{localUser.full_name || localUser.email.split('@')[0]}</p>
      </div>

      <div className="dashboard-cards">
        <div className="dashboard-card">
          <p className="dashboard-label">رقم الحساب</p>
          <p className="dashboard-value">{localUser.id}</p>
        </div>

        <div className="dashboard-card">
          <p className="dashboard-label">البريد الإلكتروني</p>
          <p className="dashboard-value">{localUser.email}</p>
        </div>

        <div className="dashboard-card">
          <p className="dashboard-label">الدور</p>
          <p className="dashboard-value">{localUser.role === 'admin' ? 'محامي' : 'مستخدم'}</p>
        </div>

        <div className="dashboard-card">
          <p className="dashboard-label">الاسم الكامل</p>
          {isEditing ? (
            <input 
              type="text" 
              value={fullName} 
              onChange={e => setFullName(e.target.value)} 
              className="messageInput"
              style={{marginTop: '0.5rem'}}
            />
          ) : (
            <p className="dashboard-value">{localUser.full_name || '—'}</p>
          )}
        </div>

        <div className="dashboard-card">
          <p className="dashboard-label">رقم الجوال</p>
          {isEditing ? (
            <input 
              type="text" 
              value={phone} 
              onChange={e => setPhone(e.target.value)} 
              className="messageInput"
              style={{marginTop: '0.5rem'}}
            />
          ) : (
            <p className="dashboard-value">{localUser.phone || '—'}</p>
          )}
        </div>
      </div>

      <div className="dashboard-action" style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
        {isEditing ? (
          <>
            <button onClick={handleSave} disabled={saving} style={{ background: '#059669' }}>
              {saving ? 'جاري الحفظ...' : 'حفظ البيانات'}
            </button>
            <button onClick={() => setIsEditing(false)} style={{ background: '#DC2626' }}>
              إلغاء
            </button>
          </>
        ) : (
          <button onClick={() => setIsEditing(true)}>
            تعديل البيانات الشخصية
          </button>
        )}
        <button onClick={() => navigate('/analyze')} style={{ background: '#3b82f6' }}>
          ابدأ تحليل عقد جديد
        </button>
      </div>

      {localUser.role === 'admin' && (
        <div className="dashboard-lawyer-section" style={{ marginTop: '2rem' }}>
          <h2 className="dashboard-lawyer-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            بيانات المحامي
          </h2>
          <div className="dashboard-cards">
            <div className="dashboard-card">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#5B21B6" strokeWidth="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
              <p className="dashboard-label">اسم المكتب</p>
              <p className="dashboard-value">—</p>
            </div>
            <div className="dashboard-card">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#5B21B6" strokeWidth="1.5"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
              <p className="dashboard-label">رخصة المزاولة</p>
              <p className="dashboard-value">—</p>
            </div>
            <div className="dashboard-card">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#5B21B6" strokeWidth="1.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.4 2 2 0 0 1 3.6 1.22h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.6a16 16 0 0 0 6.29 6.29l.54-.54a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              <p className="dashboard-label">رقم التواصل</p>
              <p className="dashboard-value">—</p>
            </div>
          </div>
          <div className="dashboard-action">
            <button onClick={() => navigate('/lawyer-profile')}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              تعديل بيانات المكتب
            </button>
          </div>
        </div>
      )}
    </div>
  )
}