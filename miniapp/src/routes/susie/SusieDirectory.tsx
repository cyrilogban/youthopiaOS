import React from 'react';
import { Card, Pill, SectionTitle } from '../../components/ui';
import { ASSISTANTS, COMMUNITY_SPACES } from '../../data/community';

export const SusieDirectory: React.FC = () => (
  <div className="section-stack">
    <section className="page-heading">
      <h1>Who is who.</h1>
      <p>Our five assistants, each with a clear job, plus the places we gather.</p>
    </section>

    <section className="section-group">
      <SectionTitle eyebrow="Assistants" right={<Pill color="purple">5 active</Pill>}>The assistant family</SectionTitle>
      <div style={{ display: 'grid', gap: 10 }}>
        {ASSISTANTS.map((assistant) => (
          <Card key={assistant.handle} style={{ padding: 16 }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
              <span className="profile-avatar" style={{ width: 42, height: 42, fontSize: 19, flexShrink: 0 }}>
                {assistant.emoji}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <strong style={{ fontSize: 14 }}>{assistant.short}</strong>
                <p className="muted-copy" style={{ marginTop: 4 }}>{assistant.responsibility}</p>
                <span style={{ display: 'inline-block', marginTop: 8, color: 'var(--accent)', fontSize: 11, fontWeight: 750 }}>
                  {assistant.handle}
                </span>
              </div>
              <a className="secondary-button" href={assistant.link} target="_blank" rel="noreferrer" style={{ minHeight: 44, paddingInline: 13 }}>
                Open
              </a>
            </div>
          </Card>
        ))}
      </div>
    </section>

    <section className="section-group">
      <SectionTitle eyebrow="Say hello">Community places</SectionTitle>
      {COMMUNITY_SPACES.map((space) => (
        <a key={space.name} className="feature-row" href={space.link} target="_blank" rel="noreferrer">
          <span style={{ minWidth: 0 }}>
            <strong>{space.name}</strong>
            <span>{space.role}</span>
          </span>
          <span className="feature-row-arrow">→</span>
        </a>
      ))}
    </section>
  </div>
);
