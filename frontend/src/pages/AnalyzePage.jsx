import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function AnalyzePage() {
  const navigate = useNavigate()
  const [contractText, setContractText] = useState('')
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [errorMessage, setErrorMessage] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!contractText.trim() && !file) {
      setStatus('error')
      setErrorMessage('الصق نص العقد أو ارفع ملف')
      return
    }
    setStatus('loading')

    const formData = new FormData()
    if (file) formData.append('file', file)
    if (contractText) formData.append('text', contractText)
    formData.append('language', 'ar')

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      navigate('/result', { state: { result: data } })
    } catch {
      setStatus('error')
      setErrorMessage('حدث خطأ في الاتصال، حاول مرة أخرى')
    }
  }

  return (
    <div>
      <div className='head-Analyze'>
        <h1 className='Title'>ارفع عقدك ودعنا نحلله</h1>
        <h3 className='under_title'>اختر نوع العقد، ارفعه، اطرح سؤالك إن وجد</h3>
      </div>

      <div className='button-Analyze'>
        <button className='TypeOf-Analyze'>عقد توظيف</button>
        <button className='TypeOf-Analyze'>عقد إنهاء خدمة</button>
        <button className='TypeOf-Analyze'>عقد خاص بالراتب</button>
      </div>

      <form onSubmit={handleSubmit}>
        <div className='sendFile-Analyze'>
          <label htmlFor="contract">ارفع العقد (PDF)</label>
          <input
            type="file"
            id="contract"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
        </div>

        <div className='sendFile-Analyze'>
          <h3 className='under_title'>أو الصق نص العقد هنا</h3>
          <textarea
            rows={4}
            placeholder="الصق نص عقدك هنا..."
            value={contractText}
            onChange={(e) => setContractText(e.target.value)}
          />
          {status === 'error' && <p style={{color:'red'}}>{errorMessage}</p>}
          <button type="submit" disabled={status === 'loading'}>
            {status === 'loading' ? 'جاري التحليل...' : 'تحليل'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default AnalyzePage