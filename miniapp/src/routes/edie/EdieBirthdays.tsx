import React from 'react';
import { Card, Pill, SectionTitle, EmptyState } from '../../components/ui';

const edieLink = (payload: string) => `https://t.me/ediecalendarbot?start=${payload}`;

export const EdieBirthdays: React.FC = () => (
  <div className="section-stack">
    <section className="page-heading">
      <h1>Birthday celebrations.</h1>
      <p>We love celebrating our YouTopians. Add your birthday and let the community rejoice with you.</p>
    </section>

    <EmptyState
      title="Add your birthday"
      body="Register your birthday with Edie and our community will celebrate you on the day. Just the month and day, never the year."
      action={
        <a className="primary-button" href={edieLink('birthday')} target="_blank" rel="noreferrer">
          Add my birthday
        </a>
      }
    />

    <section className="section-group">
      <SectionTitle eyebrow="How it works" right={<Pill color="purple">Simple</Pill>}>Birthday shoutouts</SectionTitle>
      <Card style={{ padding: 16 }}>
        <p className="muted-copy" style={{ margin: 0 }}>
          When your day comes around, Edie announces it to the community and everyone gets to share the joy with you.
          You can update or remove your birthday any time by asking Edie directly.
        </p>
        <a className="secondary-button" href={edieLink('events')} target="_blank" rel="noreferrer" style={{ marginTop: 12, width: '100%' }}>
          Open Edie in Telegram
        </a>
      </Card>
    </section>
  </div>
);
