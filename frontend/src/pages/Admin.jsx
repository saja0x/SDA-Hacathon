// Admin-only page. Unlike the dashboard, this one fetches data on
// mount: stats and the full user list, both from endpoints that return
// 403 for anyone whose role isn't "admin".

import { useEffect, useState } from 'react'
import { apiRequest } from '../api'
import { useAuth } from '../AuthContext'

export default function Admin() {
  const { token } = useAuth()
  const [users, setUsers] = useState([])
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    // Two independent admin calls; Promise.all fires them in parallel
    // instead of waiting on one before starting the other.
    Promise.all([
      apiRequest('/admin/users', { token }),
      apiRequest('/admin/stats', { token }),
    ])
      .then(([userList, statData]) => {
        setUsers(userList)
        setStats(statData)
      })
      .catch((err) => setError(err.message))
  }, [token])

  return (
    <div className="card">
      <h1>Admin panel</h1>
      {error && <p className="error">{error}</p>}

      {stats && (
        <p>
          <strong>{stats.total_users}</strong> accounts total:{' '}
          {stats.admins} admin(s), {stats.regular_users} regular user(s).
        </p>
      )}

      <p>All registered users, fetched from an admin-only endpoint:</p>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
