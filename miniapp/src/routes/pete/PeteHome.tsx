import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppData } from '../../context/AppData';
import { Card, Pill, ProgressBar, SectionTitle } from '../../components/ui';
import { SAFETY_FEATURES, trustTier } from '../../data/safety';

export const PeteHome: React.FC = () => {
  const navigate = useNavigate();
  const { user, profile } = useAppData();
  const trust = profile.status === 'ok' ? profile.profile.trustScore ?? 100 : 100;
  const tier = trustTier(trust);
  const clean = trust >= 100;
  const name = user?.firstName || 'friend';

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Safe to gather, {name}.</h1>
        <p>I'm Pete. I verify new members, keep spam and raids out, and hold the line so fellowship stays peaceful.</p>
      </section>

      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span className="profile-avatar" style={{ width: 52, height: 52, fontSize: 22 }}>
            🛡️
          </span>
          <div>
            <strong style={{ fontSize: 15 }}>Peter, the guardian</strong>
            <p className="muted-copy" style={{ marginTop: 3 }}>All quiet on my watch</p>
          </div>
          <span style={{ marginLeft: 'auto' }}>
            <Pill color={clean ? 'success' : 'warning'}>{clean ? 'Clean record' : 'Under review'}</Pill>
          </span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: 18 }}>
          <div>
            <div className="metric-label">Trust score</div>
            <div style={{ fontSize: 30, fontWeight: 800, lineHeight: 1.1 }}>
              {trust}
              <span style={{ color: 'var(--text-muted)', fontSize: 15, fontWeight: 700 }}> / 100</span>
            </div>
          </div>
          <Pill color={tier.tone}>{tier.label}</Pill>
        </div>
        <div style={{ marginTop: 12 }}>
          <ProgressBar value={trust} max={100} tone={clean ? 'success' : 'purple'} />
        </div>
        <p className="muted-copy" style={{ marginTop: 10 }}>{tier.description}</p>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Under the hood" right={<Pill color="purple">Always on</Pill>}>How I protect us</SectionTitle>
        <div style={{ display: 'grid', gap: 10 }}>
          {SAFETY_FEATURES.map((feature) => (
            <Card key={feature.title} style={{ padding: 16 }}>
              <strong style={{ fontSize: 14 }}>{feature.title}</strong>
              <p className="muted-copy" style={{ marginTop: 4 }}>{feature.description}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Know the line">Community rules</SectionTitle>
        <Card style={{ padding: 16 }}>
          <p className="muted-copy" style={{ margin: 0 }}>
            A short, clear list keeps this a peaceful place for everyone. Read them once and you're set.
          </p>
          <button className="primary-button" onClick={() => navigate('/pete/rules')} style={{ marginTop: 12, width: '100%' }}>
            Read the rules
          </button>
        </Card>
      </section>
    </div>
  );
};
