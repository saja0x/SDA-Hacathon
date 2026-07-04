import React from 'react';

const DUMMY_LAWYERS = [
  {
    id: 1,
    name: 'أحمد عبدالله السالم',
    specialty: 'عقود تجارية وعمالية',
    license: '43★★★★',
    phone: '05★★★★★★★',
    price: '500 ريال / ساعة',
    rating: 4.9,
  },
  {
    id: 2,
    name: 'مكتب نورة القحطاني للمحاماة',
    specialty: 'تسوية النزاعات والتحكيم',
    license: '41★★★★',
    phone: '05★★★★★★★',
    price: '700 ريال / ساعة',
    rating: 4.7,
  },
  {
    id: 3,
    name: 'فهد محمد الدوسري',
    specialty: 'ملكية فكرية وعقود تقنية',
    license: '42★★★★',
    phone: '05★★★★★★★',
    price: '600 ريال / ساعة',
    rating: 4.8,
  }
];

export default function LawyersPage() {
  return (
    <div className="community-page">
      <div className="community-hero" style={{ background: 'var(--ink2)' }}>
        <h1>دليل المحامين المعتمدين</h1>
        <p>تواصل مع نخبة من المحامين المتخصصين في صياغة ومراجعة العقود</p>
      </div>

      <div className="lawyers-list">
        {DUMMY_LAWYERS.map(lawyer => (
          <div key={lawyer.id} className="community-post-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
            <div className="community-post-header">
              <strong>{lawyer.name}</strong>
              <span className="community-score" style={{ background: 'var(--abg)', color: 'var(--gold)', border: '1px solid #F0C96E' }}>
                ⭐ {lawyer.rating}
              </span>
            </div>
            <p className="community-post-message" style={{ margin: 0 }}>
              <strong style={{ color: 'var(--muted)' }}>التخصص:</strong> {lawyer.specialty}
            </p>
            <p className="community-post-message" style={{ margin: 0 }}>
              <strong style={{ color: 'var(--muted)' }}>رقم الترخيص:</strong> {lawyer.license}
            </p>
            <p className="community-post-message" style={{ margin: 0 }}>
              <strong style={{ color: 'var(--muted)' }}>تكلفة الاستشارة:</strong> {lawyer.price}
            </p>
            <div style={{ marginTop: '0.5rem' }}>
              <span style={{
                display: 'inline-block',
                background: 'var(--ink2)',
                color: 'white',
                padding: '0.5rem 1.5rem',
                borderRadius: '6px',
                fontWeight: 'bold',
                fontSize: '0.9rem',
                cursor: 'default',
                opacity: 0.7
              }}>
                05★★★★★★★
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}