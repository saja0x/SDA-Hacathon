import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() { logout(); navigate('/login') }

  return (
    <nav className="navbar">
      <span className="brand">Code Cortex</span>
      <div className="nav-links">
        <Link to="/contract">الرئيسية</Link>
        <Link to="/analyze">تحليل عقد</Link>
        <Link to="/community">المجتمع</Link>
        <Link to="/lawyers">المحامين</Link>
        {user ? (
          <div style={{display:'flex',alignItems:'center',gap:'1rem',marginRight:'auto'}}>
            <button onClick={handleLogout} style={{background:'transparent',color:'var(--muted)',border:'1px solid var(--border)'}}>
              تسجيل الخروج
            </button>
            <Link to="/dashboard" style={{textDecoration:'none'}}>
              <div style={{display:'flex',alignItems:'center',gap:'8px',background:'var(--p3)',padding:'4px 12px 4px 4px',borderRadius:'24px',border:'1px solid #C7D2FE',cursor:'pointer',transition:'all .2s'}}>
                <div style={{width:'36px',height:'36px',background:'var(--g1)',color:'white',borderRadius:'12px',display:'flex',alignItems:'center',justifyContent:'center',fontWeight:'bold',fontSize:'1.1rem'}}>
                  {user.full_name ? user.full_name[0] : user.email[0].toUpperCase()}
                </div>
              </div>
            </Link>
          </div>
        ) : (
          <div style={{display:'flex',alignItems:'center',gap:'.75rem',marginRight:'auto'}}>
            <button onClick={() => navigate('/login')}>تسجيل الدخول</button>
            <button onClick={() => navigate('/register')} style={{background:'var(--g1)',color:'#fff',border:'none'}}>إنشاء حساب</button>
          </div>
        )}
      </div>
    </nav>
  )
}