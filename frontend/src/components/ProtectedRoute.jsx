// The frontend half of route protection. This component decides what
// to render based on auth state:
//
//   still checking the stored token  -> a loading message
//   not logged in                    -> redirect to /login
//   logged in but not admin (when adminOnly) -> redirect to /dashboard
//   otherwise                        -> the actual page
//
// Important caveat for students: this is UX, not security. Anyone can
// open DevTools and fiddle with React state. The real enforcement is
// the backend returning 401/403 -- this component just keeps honest
// users out of pages that would only show them errors.

import { Navigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth()

  // On a page refresh there's a brief window where we have a token but
  // haven't confirmed it with the backend yet. Render a placeholder
  // instead of redirecting -- otherwise every refresh would flash the
  // login page.
  if (loading) {
    return <p>Loading...</p>
  }

  if (!user) {
    // "replace" swaps the current history entry instead of pushing a
    // new one, so the back button doesn't take you to a page you were
    // just kicked out of.
    return <Navigate to="/login" replace />
  }

  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return children
}
