import React from 'react';
import { Card, Pill, SectionTitle } from '../../components/ui';
import { RULES } from '../../data/safety';

export const PeteRules: React.FC = () => (
  <div className="section-stack">
    <section className="page-heading">
      <h1>House rules.</h1>
      <p>Short and clear, so everyone can gather in peace.</p>
    </section>

    <section className="section-group">
      <SectionTitle eyebrow="Read once, keep always" right={<Pill color="purple">{RULES.length} rules</Pill>}>
        Our guidelines
      </SectionTitle>
      <div style={{ display: 'grid', gap: 10 }}>
        {RULES.map((rule, index) => (
          <Card key={rule.title} style={{ padding: 16 }}>
            <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span
                style={{
                  width: 26,
                  height: 26,
                  borderRadius: '50%',
                  background: 'var(--accent-soft)',
                  color: 'var(--accent)',
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: 12,
                  fontWeight: 800,
                  flexShrink: 0,
                }}
              >
                {index + 1}
              </span>
              <div>
                <strong style={{ fontSize: 14 }}>{rule.title}</strong>
                <p className="muted-copy" style={{ marginTop: 4 }}>{rule.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </section>

    <p className="muted-copy">
      Questions about a rule or a decision? Appeal calmly through Pete, and the admins will take it from there.
    </p>
  </div>
);
