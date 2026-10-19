import React, { useState } from 'react';
import { Card } from '../../components/ui';
import { FAQS } from '../../data/community';

export const SusieFaq: React.FC = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Questions, answered.</h1>
        <p>Everything you might want to know about YouThopia Bible Community.</p>
      </section>

      <Card style={{ padding: 18 }}>
        <div style={{ display: 'grid', gap: 8 }}>
          {FAQS.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div key={index} style={{ borderBottom: index < FAQS.length - 1 ? '1px solid var(--slate-100)' : undefined, paddingBottom: 8 }}>
                <button
                  onClick={() => setOpenIndex(isOpen ? null : index)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    background: 'none',
                    border: 0,
                    padding: '8px 0',
                    fontSize: 13,
                    fontWeight: 700,
                    color: 'var(--ink)',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: 12,
                  }}
                >
                  <span>{faq.question}</span>
                  <span style={{ color: isOpen ? 'var(--accent)' : 'var(--text-muted)', fontSize: 18, fontWeight: 700, flexShrink: 0 }}>
                    {isOpen ? '−' : '+'}
                  </span>
                </button>
                <div style={{ maxHeight: isOpen ? 240 : 0, overflow: 'hidden', transition: 'max-height 0.25s var(--ease)' }}>
                  <p className="muted-copy" style={{ margin: '2px 0 6px 0' }}>{faq.answer}</p>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
};
