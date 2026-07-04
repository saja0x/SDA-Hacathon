import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Admin from './pages/Admin'
import ContractPage from './pages/ContractPage'
import AnalyzePage from './pages/AnalyzePage'
import ResultPage from './pages/RsultPage'
import CommunityPage from './pages/CommunityPage'
import LawyersPage from './pages/LawyersPage'
import './index.css'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/contract" element={<ContractPage />} />
         <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="/community" element={<ProtectedRoute><CommunityPage /></ProtectedRoute>} />
          <Route path="/lawyers" element={<LawyersPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute adminOnly><Admin /></ProtectedRoute>} />
          <Route path="/" element={<Navigate to="/contract" replace />} />
          <Route path="*" element={<Navigate to="/contract" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}