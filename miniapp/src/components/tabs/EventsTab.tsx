import React, { useEffect, useState } from 'react';
import { fetchEvents, type EventItem } from '../../services/api';
import { Card, Pill, SectionTitle, Skeleton } from '../ui';

const eventLink = 'https://t.me/ediecalendarbot?start=calendar';

export const EventsTab: React.FC = () => {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const results = await fetchEvents();
      if (!cancelled) {
        setEvents(results);
        setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const next = events[0];
  const remaining = events.slice(1);

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">Edie's calendar</span>
        <h1>Make room for fellowship.</h1>
        <p>Keep the next gathering close, set reminders, and arrive ready for the moments that matter.</p>
      </section>

      {loading ? (
        <Card style={{ padding: 20 }}><Skeleton height={14} width="32%" /><Skeleton height={28} style={{ marginTop: 16 }} /><Skeleton height={18} width="78%" style={{ marginTop: 8 }} /></Card>
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
          <a className="primary-button" href={eventLink} target="_blank" rel="noreferrer" style={{ marginTop: 18 }}>RSVP with Edie</a>
        </Card>
      ) : (
        <Card style={{ padding: 20 }}><p className="muted-copy">There are no upcoming gatherings just yet. Check back soon.</p></Card>
      )}

      <section className="section-group">
        <SectionTitle eyebrow="Coming up" right={<Pill color="slate">{events.length} events</Pill>}>Plan your week</SectionTitle>
        {loading ? (
          <div style={{ display: 'grid', gap: 10 }}>{[1, 2].map((item) => <Skeleton key={item} height={78} />)}</div>
        ) : remaining.length ? (
          <div style={{ display: 'grid', gap: 10 }}>
            {remaining.map((event) => (
              <Card key={`${event.id ?? event.title}-${event.startsAt}`} style={{ padding: 16 }}>
                <div className="eyebrow">{event.category ?? 'Community'}</div>
                <strong style={{ display: 'block', marginTop: 5, fontSize: 15 }}>{event.title}</strong>
                <p className="muted-copy" style={{ marginTop: 5 }}>{event.startsAt} · {event.location ?? 'YouThopia'}</p>
              </Card>
            ))}
          </div>
        ) : (
          <Card style={{ padding: 16 }}><p className="muted-copy">Your next events will appear here after the featured gathering.</p></Card>
        )}
      </section>

      <Card style={{ padding: 18 }}>
        <SectionTitle eyebrow="Keep connected">Manage through Edie</SectionTitle>
        <div className="inline-actions">
          <a className="secondary-button" href={eventLink} target="_blank" rel="noreferrer">My events</a>
          <a className="secondary-button" href="https://t.me/ediecalendarbot?start=birthday" target="_blank" rel="noreferrer">Add birthday</a>
        </div>
      </Card>
    </div>
  );
};
