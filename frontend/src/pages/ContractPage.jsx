import { useNavigate } from 'react-router-dom'

export default function ContractPage() {
  const navigate = useNavigate()
  return (
    <div className="ContractInterface">
      <div className='head1-info'>
        <h1 className='Title'>اعرف حقوقك</h1>
        <h3 className='under_title'>ارفع عقدك ودعنا نشرحه لك بلغة بسيطة — بدون مصطلحات معقدة</h3>
      <button onClick={() => navigate('/analyze')}>ابدأ التحليل مجاناً</button>
      </div>
      <div className='content-info'>
        <h4 className='ex1'>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          تحليل خلال وقت قصير
        </h4>
        <h4 className='ex2'>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          آمن وخاص 100%
        </h4>
        <h4 className='ex3'>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          عربي وإنجليزي
        </h4>
      </div>
      <div className='down'>
        <h1 className='Title'>كل ما تحتاجه لتفهم عقدك</h1>
        <h3 className='under_title'>ثلاث خطوات بسيطة، ونتائج فورية</h3>
        <div className='cards-row'>
          <h4 className='ex4'>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" strokeWidth="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            افهم عقدك
          </h4>
          <h4 className='ex5'>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
            اعرف حقوقك
          </h4>
          <h4 className='ex6'>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            اكتشف البنود الخطرة
          </h4>
        </div>
      </div>
    </div>
  )
}