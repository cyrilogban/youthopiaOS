import React from 'react';
import { Card, Pill, SectionTitle, EmptyState } from '../../components/ui';

const edieLink = (payload: string) => `https://t.me/ediecalendarbot?start=${payload}`;

const RSVP_STEPS = [
  { step: '01', title: 'Find a gathering', description: 'Browse the calendar and open the one you want to attend.' },
  { step: '02', title: 'Pick an answer', description: 'Choose Yes, Maybe, or No so the team can plan.' },
  { step: '03', title: 'Get reminded', description: 'Edie nudges you before it starts, so you never miss it.' },
];

export const EdieMyEvents: React.FC = () => (
  <div className="section-stack">
    <section className="page-heading">
      <h1>Your RSVPs.</h1>
      <p>The gatherings you have answered for, all in one place.</p>
    </section>

    <EmptyState
      title="No events yet"
      body="Once you RSVP to a gathering, it will show up here so you can keep track of your week."
      action={
        <a className="primary-button" href={edieLink('calendar')} target="_blank" rel="noreferrer">
          Browse the calendar
        </a>
      }
    />

    <section className="section-group">
      <SectionTitle eyebrow="How it works" right={<Pill color="purple">3 steps</Pill>}>Responding to a gathering</SectionTitle>
      <Card style={{ padding: 16 }}>
        <div style={{ display: 'grid', gap: 12 }}>
          {RSVP_STEPS.map((item) => (
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
        <a className="secondary-button" href={edieLink('events')} target="_blank" rel="noreferrer" style={{ marginTop: 14, width: '100%' }}>
          Open my events in Edie
        </a>
      </Card>
    </section>
  </div>
);
