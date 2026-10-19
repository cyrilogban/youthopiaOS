import React from 'react';
import { useAppData } from '../../context/AppData';
import { Card, Pill, ProgressBar, SectionTitle } from '../../components/ui';
import { TRUST_EVENTS, TRUST_TIERS, trustTier } from '../../data/safety';

export const PeteTrust: React.FC = () => {
  const { profile } = useAppData();
  const trust = profile.status === 'ok' ? profile.profile.trustScore ?? 100 : 100;
  const current = trustTier(trust);

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Your Trust Score.</h1>
        <p>A single number out of 100 that reflects your reliability and integrity across the community.</p>
      </section>

      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <div className="metric-label">Current score</div>
            <div style={{ fontSize: 34, fontWeight: 800, lineHeight: 1.1 }}>
              {trust}
              <span style={{ color: 'var(--text-muted)', fontSize: 15, fontWeight: 700 }}> / 100</span>
            </div>
          </div>
          <Pill color={current.tone}>{current.label}</Pill>
        </div>
        <div style={{ marginTop: 12 }}>
          <ProgressBar value={trust} max={100} tone={trust >= 100 ? 'success' : 'purple'} />
        </div>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Standing" right={<Pill color="slate">3 bands</Pill>}>How you are rated</SectionTitle>
        <div style={{ display: 'grid', gap: 10 }}>
          {TRUST_TIERS.map((tier) => {
            const active = tier.label === current.label;
            return (
              <Card key={tier.label} style={{ padding: 16, borderColor: active ? 'var(--accent)' : undefined }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
                  <strong style={{ fontSize: 14 }}>{tier.label}</strong>
                  <Pill color={tier.tone}>{tier.min}+</Pill>
                </div>
                <p className="muted-copy" style={{ marginTop: 4 }}>{tier.description}</p>
              </Card>
            );
          })}
        </div>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="The ledger" right={<Pill color="purple">Transparent</Pill>}>What moves your score</SectionTitle>
        <Card style={{ padding: 8 }}>
          {TRUST_EVENTS.map((event, index) => (
            <div
              key={event.action}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                gap: 12,
                alignItems: 'center',
                padding: '12px 8px',
                borderBottom: index < TRUST_EVENTS.length - 1 ? '1px solid var(--slate-100)' : undefined,
              }}
            >
              <div style={{ minWidth: 0 }}>
                <strong style={{ fontSize: 13 }}>{event.action}</strong>
                <p className="muted-copy" style={{ marginTop: 2 }}>{event.note}</p>
              </div>
              <strong style={{ color: event.delta >= 0 ? 'var(--success)' : 'var(--danger, #C0392B)', fontSize: 14, whiteSpace: 'nowrap' }}>
                {event.delta >= 0 ? `+${event.delta}` : event.delta}
              </strong>
            </div>
          ))}
        </Card>
      </section>

      <p className="muted-copy">
        Scores are capped at 100. Every action is logged, and an accepted appeal restores you to full standing.
      </p>
    </div>
  );
};
