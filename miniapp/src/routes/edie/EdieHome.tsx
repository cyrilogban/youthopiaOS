import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchEvents, type EventItem } from '../../services/api';
import { Card, Pill, SectionTitle, Skeleton } from '../../components/ui';

const edieLink = (payload: string) => `https://t.me/ediecalendarbot?start=${payload}`;

export const EdieHome: React.FC = () => {
  const navigate = useNavigate();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void fetchEvents().then((results) => {
      if (!cancelled) {
        setEvents(results);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const next = events[0];

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Never miss a gathering.</h1>
        <p>I'm Edie. I keep the calendar, so studies, prayer calls, and celebrations always find you in time.</p>
      </section>

      {loading ? (
        <Card style={{ padding: 20 }}>
          <Skeleton height={14} width="32%" />
          <Skeleton height={26} style={{ marginTop: 16 }} />
          <Skeleton height={18} width="78%" style={{ marginTop: 8 }} />
        </Card>
      ) : next ? (
        <Card style={{ padding: 20, background: 'var(--grad-quiet)', borderColor: 'var(--purple-200)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 14, alignItems: 'flex-start' }}>
            <div>
              <div className="eyebrow">Next gathering</div>
              <h2 style={{ margin: '6px 0 0', fontSize: 22, lineHeight: 1.18 }}>{next.title}</h2>
            </div>
            <Pill color="purple">{next.category ?? 'Community'}</Pill>
          </div>
          <p className="muted-copy" style={{ marginTop: 10 }}>{next.startsAt}</p>
          <p className="muted-copy" style={{ marginTop: 4 }}>{next.location ?? 'YouThopia community'}</p>
          <a className="primary-button" href={next.id ? edieLink(`rsvp_${next.id}`) : edieLink('rsvp')} target="_blank" rel="noreferrer" style={{ marginTop: 18 }}>
            RSVP with Edie
          </a>
        </Card>
      ) : (
        <Card style={{ padding: 20 }}>
          <p className="muted-copy">There are no upcoming gatherings just yet. Check back soon.</p>
        </Card>
      )}

      <section className="section-group">
        <SectionTitle eyebrow="Your calendar" right={<Pill color="slate">In app</Pill>}>Where to go</SectionTitle>
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'grid', gap: 10 }}>
            <button className="secondary-button" onClick={() => navigate('/edie/calendar')} style={{ width: '100%' }}>
              View the weekly calendar
            </button>
            <button className="secondary-button" onClick={() => navigate('/edie/my-events')} style={{ width: '100%' }}>
              See my RSVPs
            </button>
            <button className="secondary-button" onClick={() => navigate('/edie/birthdays')} style={{ width: '100%' }}>
              Birthday celebrations
            </button>
          </div>
        </Card>
      </section>

      <Card style={{ padding: 16 }}>
        <SectionTitle eyebrow="Stay ready">Reminders</SectionTitle>
        <p className="muted-copy" style={{ margin: 0 }}>
          Edie sends a daily reminder and can nudge you before each gathering. Toggle reminders any time in her DM.
        </p>
        <a className="secondary-button" href={edieLink('events')} target="_blank" rel="noreferrer" style={{ marginTop: 12, width: '100%' }}>
          Open Edie in Telegram
        </a>
      </Card>
    </div>
  );
};
