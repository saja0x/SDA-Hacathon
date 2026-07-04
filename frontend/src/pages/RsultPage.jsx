import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

function ResultPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const result = location.state?.result

  const [messages, setMessages] = useState([{
    role: 'bot',
    text: 'أهلاً! قرأت عقدك ومستعد للإجابة عن أي سؤال. اختر من الأسئلة المقترحة أو اكتب سؤالك بالأسفل'
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const items = [
  result?.risk_level === 'high' ? 'خطر عالي' : result?.risk_level === 'medium' ? 'خطر متوسط' : 'آمن',
  `درجة الأمان: ${result?.shield_score ?? '—'}`,
  `البنود الخطرة: ${result?.red_flags?.length ?? 0}`,
  `البنود الجيدة: ${result?.good_clauses?.length ?? 0}`,
]
  async function sendMessage(text) {
    const userText = text || input.trim()
    if (!userText) return

    setInput('')
    setMessages(p => [...p, { role: 'user', text: userText }])
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('contract', result?.contract_text || '')
      formData.append('question', userText)
      formData.append('history', JSON.stringify(
        messages
          .filter((m, idx) => !(m.role === 'bot' && idx === 0))
          .map(m => ({ role: m.role === 'bot' ? 'assistant' : 'user', content: m.text }))
      ))

      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      setMessages(p => [...p, { role: 'bot', text: data.answer || 'عذراً، لم أتمكن من الرد.' }])
    } catch {
      setMessages(p => [...p, { role: 'bot', text: 'حدث خطأ في الاتصال، حاول مرة أخرى.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ResultInterface">

      <div className='head-Result'>

        <h4 className='left'>
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
  اكتمل التحليل
</h4>
<h4 className='right'>
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
  {result ? 'عقدك' : 'employment_contract.pdf'}
</h4>

        <div className='Terms'>
          {items.map((text, index) => (
            <div key={index} className="grid-Terms">{text}</div>
          ))}
        </div>

        <div className='reviwe'>
         <h4 className='re1'>
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
  ملخّص بلغة بسيطة
</h4>
        </div>

        <h4 className='lawx'>
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#DC2626" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
  البنود الخطرة
</h4>
        <div className='Law'>
          {result?.red_flags?.length > 0 ? (
            result.red_flags.map((flag, i) => (
              <div key={i} className="grid-Law" style={{background:'#FEF2F2', color:'#DC2626', border:'1px solid #FECACA', textAlign:'right', padding:'1rem', borderRadius:'12px'}}>
                <strong>{flag.clause}</strong>
                <p style={{fontSize:'0.85rem', marginTop:'0.3rem'}}>{flag.reason}</p>
              </div>
            ))
          ) : (
            <div className="grid-Law">لا توجد بنود خطرة</div>
          )}
        </div>

        <h4 className='lawx'>
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"/></svg>
  البنود الجيدة
</h4>
        <div className='Law'>
          {result?.good_clauses?.length > 0 ? (
            result.good_clauses.map((clause, i) => (
              <div key={i} className="grid-Law" style={{background:'#F0FDF4', color:'#059669', border:'1px solid #BBF7D0', textAlign:'right', padding:'1rem', borderRadius:'12px'}}>
                {clause}
              </div>
            ))
          ) : (
            <div className="grid-Law">—</div>
          )}
        </div>

     <h4 className='lawx'>
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D97706" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
  النصيحة
</h4>
        <div className='reviwe'>
          <p>{result?.overall_advice || '—'}</p>
        </div>
      </div>

      <div className="Chat-box">

        <div className='QA-Analyze'>
          <h3>هل لديك سؤال محدد؟</h3>
          <button onClick={() => sendMessage('ما هي أخطر بنود هذا العقد؟')}>ما أخطر البنود؟</button>
          <button onClick={() => sendMessage('ما هي حقوقي في هذا العقد؟')}>ما هي حقوقي؟</button>
          <button onClick={() => sendMessage('هل يمكنني التفاوض على هذا العقد؟')}>كيف أتفاوض؟</button>
        </div>

        <div className='Chat-box-messages'>
          {messages.map((msg, i) => (
            <div key={i} className={msg.role === 'user' ? 'AimessageAppear user-msg' : 'AimessageAppear'}>
              <p className='messageAi'>{msg.text}</p>
            </div>
          ))}
          {loading && (
            <div className='AimessageAppear'>
              <p className='messageAi'>جاري التفكير...</p>
            </div>
          )}
        </div>

        <div className='Chatfooter'>
          <form action='#' className='chat-form' onSubmit={(e) => { e.preventDefault(); sendMessage() }}>
            <input
              type="text"
              placeholder='اكتب سؤالك...'
              className='messageInput'
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
            />
            <button className='submit' type="submit" disabled={loading || !input.trim()}>
              إرسال
            </button>
          </form>
        </div>

      </div>
    </div>
  )
}

export default ResultPage