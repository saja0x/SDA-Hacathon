import { useState, useEffect } from 'react'
 
export default function CommunityPage() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [name, setName] = useState('')
  const [message, setMessage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
 
  useEffect(() => {
    fetch('http://localhost:8000/community')
      .then(res => res.json())
      .then(data => { setPosts(data.posts); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])
 
  async function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim() || !message.trim()) return
    setSubmitting(true)
    setError('')
 
    const formData = new FormData()
    formData.append('name', name)
    formData.append('message', message)
 
    try {
      const res = await fetch('http://localhost:8000/community', {
        method: 'POST',
        body: formData
      })
      const newPost = await res.json()
      setPosts(prev => [newPost, ...prev])
      setName('')
      setMessage('')
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch {
      setError('حدث خطأ، حاول مرة أخرى')
    } finally {
      setSubmitting(false)
    }
  }
 
  function riskColor(level) {
    if (level === 'high') return { background: '#FEF2F2', color: '#DC2626', border: '1px solid #FECACA' }
    if (level === 'medium') return { background: '#FFFBEB', color: '#D97706', border: '1px solid #FDE68A' }
    if (level === 'low') return { background: '#F0FDF4', color: '#059669', border: '1px solid #BBF7D0' }
    return {}
  }
 
 function riskLabel(level) {
  if (level === 'high') return 'خطر عالي'
  if (level === 'medium') return 'خطر متوسط'
  if (level === 'low') return 'آمن'
  return null
}
 
  return (
    <div className="community-page">
 
      <div className="community-hero">
       <h1>
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
  هنا المجتمع 
</h1>
        <p>شارك تجربتك مع العقود وساعد غيرك يتجنب الأخطاء</p>
      </div>
 
      {/* نموذج الإضافة */}
      <div className="community-form-card">
        <h2>شارك تجربتك</h2>
        {success && <p className="community-success">تم نشر تجربتك بنجاح!</p>}
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit}>
          <label>اسمك (أو اسم مستعار)</label>
          <input
            type="text"
            placeholder="مثال: مستقل من الرياض"
            value={name}
            onChange={e => setName(e.target.value)}
            required
          />
          <label>تجربتك مع العقود</label>
          <textarea
            placeholder="شارك نصيحة أو تجربة حقيقية مع عقد عمل..."
            value={message}
            onChange={e => setMessage(e.target.value)}
            rows={4}
            required
          />
          <button type="submit" disabled={submitting}>
            {submitting ? 'جاري النشر...' : 'نشر التجربة'}
          </button>
        </form>
      </div>
 
      {/* المنشورات */}
      <div className="community-posts">
        <h2>التجارب </h2>
        {loading ? (
          <p style={{ textAlign: 'center', color: '#78716C' }}>جاري التحميل...</p>
        ) : posts.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#78716C' }}>لا توجد تجارب بعد — كن أول من يشارك!</p>
        ) : (
          posts.map(post => (
            <div key={post.id} className="community-post-card">
              <div className="community-post-header">
                <strong>{post.name}</strong>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {post.shield_score !== null && (
                    <span className="community-score">درجة الأمان: {post.shield_score}</span>
                  )}
                  {post.risk_level && (
                    <span className="community-risk" style={riskColor(post.risk_level)}>
                      {riskLabel(post.risk_level)}
                    </span>
                  )}
                </div>
              </div>
              <p className="community-post-message">{post.message}</p>
              <small className="community-post-date">
                {new Date(post.created_at).toLocaleDateString('ar-SA')}
              </small>
            </div>
          ))
        )}
      </div>
 
    </div>
  )
}