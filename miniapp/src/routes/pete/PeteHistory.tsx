import React from 'react';
import { Card, Pill, SectionTitle, EmptyState } from '../../components/ui';

const APPEALS = [
  { step: '01', title: 'Submit your appeal', description: 'Tell the admins what happened and why your score should be restored, in a single DM message.' },
  { step: '02', title: 'Admins review', description: 'The team reads your appeal and decides together.' },
  { step: '03', title: 'Standing restored', description: 'If accepted, your Trust Score returns to a full 100.' },
];

export const PeteHistory: React.FC = () => (
  <div className="section-stack">
    <section className="page-heading">
      <h1>Your record.</h1>
      <p>A transparent account of your standing in the community. Nothing hidden, nothing surprising.</p>
    </section>

    <EmptyState
      title="Clean record, nothing on file"
      body="No warnings or moderation actions are recorded for your account. Keep it that way and your Trust Score stays at 100."
    />

    <section className="section-group">
      <SectionTitle eyebrow="If it happens" right={<Pill color="purple">3 steps</Pill>}>How appeals work</SectionTitle>
      <Card style={{ padding: 16 }}>
        <div style={{ display: 'grid', gap: 12 }}>
          {APPEALS.map((item) => (
            <div key={item.step} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  color: 'var(--accent)',
                  background: 'var(--accent-soft)',
                  border: '1px solid var(--accent-soft)',
                  padding: '5px 9px',
                  borderRadius: 'var(--radius-md)',
                  flexShrink: 0,
                }}
              >
                {item.step}
              </span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700 }}>{item.title}</div>
                <p className="muted-copy" style={{ marginTop: 2 }}>{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </section>
  </div>
);
