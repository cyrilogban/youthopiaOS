import React, { useEffect, useState } from 'react';
import { fetchEvents, type EventItem } from '../../services/api';
import { Card, Skeleton, Pill, SectionTitle } from '../ui';

export const EventsTab: React.FC = () => {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const items = await fetchEvents();
      if (!cancelled) {
        setEvents(items);
        setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Parse a startsAt string into date parts (best effort).
  const parseDate = (raw: string) => {
    const d = new Date(raw);
    if (!isNaN(d.getTime())) {
      return {
        day: d.getDate(),
        month: d.toLocaleString('en', { month: 'short' }).toUpperCase(),
        time: d.toLocaleString('en', { hour: 'numeric', minute: '2-digit' }),
        full: d.toLocaleString('en', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }),
      };
    }
    return { day: null, month: null, time: '', full: raw };
  };

  return (
    <div className="section-stack">
      {/* Eddy Events Hero Banner */}
      <section
        style={{
          borderRadius: 28,
          padding: 20,
          color: '#ffffff',
          background: 'linear-gradient(135deg, #0e7490 0%, #0284c7 52%, #38bdf8 100%)',
          boxShadow: '0 18px 48px rgba(14, 116, 144, 0.25)',
        }}
      >
        <Pill color="deep" style={{ background: 'rgba(255,255,255,0.18)', borderColor: 'rgba(255,255,255,0.28)', marginBottom: 12 }}>
          Eddy Calendar Hub
        </Pill>
        <h2 style={{ margin: 0, fontSize: 26, lineHeight: 1.08, fontWeight: 950 }}>Fellowship Schedule & Gatherings</h2>
        <p style={{ margin: '9px 0 0', color: 'rgba(255,255,255,0.85)', fontSize: 13, lineHeight: 1.55 }}>
          Stay updated with weekly Bible studies, prayer intercessions, birthdays, and church community hangouts.
        </p>
      </section>

      {/* Upcoming Events List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <SectionTitle eyebrow="Calendar" right={<Pill color="purple">{events.length} Events</Pill>}>
          Upcoming Gatherings
        </SectionTitle>

        {loading ? (
          <Card style={{ padding: 16 }}>
            <div style={{ display: 'flex', gap: 14 }}>
              <Skeleton height={52} width={52} radius={14} />
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                <Skeleton height={12} width={80} />
                <Skeleton height={16} width="80%" />
                <Skeleton height={12} width="60%" />
              </div>
            </div>
          </Card>
        ) : events.length > 0 ? (
          events.map((evt, idx) => {
            const date = parseDate(evt.startsAt || '');
            return (
              <Card key={idx} hover style={{ padding: 16 }}>
                <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                  {date.day !== null ? (
                    <div
                      style={{
                        width: 52,
                        height: 52,
                        borderRadius: 'var(--radius-md)',
                        background: 'var(--grad-hero)',
                        color: '#fff',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        boxShadow: '0 4px 14px rgba(109,40,217,0.22)',
                      }}
                    >
                      <span style={{ fontSize: 18, fontWeight: 900, lineHeight: 1 }}>{date.day}</span>
                      <span style={{ fontSize: 10, fontWeight: 700, opacity: 0.9 }}>{date.month}</span>
                    </div>
                  ) : (
                    <div
                      style={{
                        width: 52,
                        height: 52,
                        borderRadius: 'var(--radius-md)',
                        background: 'var(--slate-100)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        fontSize: 18,
                        fontWeight: 800,
                        color: 'var(--primary-purple)',
                      }}
                    >
                      ✦
                    </div>
                  )}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span className="eyebrow" style={{ fontSize: 10 }}>
                        {evt.category || 'Community Gathering'}
                      </span>
                      <Pill color="neutral">{evt.location || 'Telegram Channel'}</Pill>
                    </div>
                    <h3 style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-color)', margin: '0 0 4px 0' }}>{evt.title}</h3>
                    <p className="muted-copy" style={{ margin: 0, fontSize: 12 }}>
                      {date.time ? date.full : evt.startsAt}
                    </p>
                    <div style={{ marginTop: 10, display: 'flex', justifyContent: 'flex-end' }}>
                      <a
                        href="https://t.me/iamedyybot?start=calendar"
                        target="_blank"
                        rel="noreferrer"
                        className="ghost-button"
                        style={{ textDecoration: 'none', height: 32, minHeight: 32, fontSize: 11, padding: '0 12px' }}
                      >
                        RSVP with Eddy →
                      </a>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })
        ) : (
          <Card style={{ padding: 18 }}>
            <div className="muted-copy">
              No upcoming events scheduled right now. Check back soon or message @iamedyybot to register your birthday!
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
