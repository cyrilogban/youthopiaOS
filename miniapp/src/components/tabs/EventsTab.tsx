import React, { useEffect, useState } from 'react';
import { fetchEvents, type EventItem } from '../../services/api';
import { Card, Skeleton, Pill } from '../ui';

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-color)', letterSpacing: '-0.02em' }}>
          Events & Schedule
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
          Powered by Eddy Bot &bull; Community Calendar & Reminders
        </p>
      </div>

      {/* Upcoming Events List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
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
              <Card key={idx} hover style={{ padding: 16, display: 'flex', gap: 14 }}>
                {date.day !== null ? (
                  <div
                    style={{
                      width: 54,
                      height: 54,
                      borderRadius: 'var(--radius-md)',
                      background: 'var(--grad-hero)',
                      color: '#fff',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      boxShadow: '0 4px 12px rgba(109,40,217,0.25)',
                    }}
                  >
                    <span style={{ fontSize: 18, fontWeight: 800, lineHeight: 1 }}>{date.day}</span>
                    <span style={{ fontSize: 10, fontWeight: 600, opacity: 0.9 }}>{date.month}</span>
                  </div>
                ) : (
                  <div
                    style={{
                      width: 54,
                      height: 54,
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
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        color: 'var(--primary-purple)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}
                    >
                      {evt.category || 'Community Gathering'}
                    </span>
                    <Pill>{evt.location || 'Telegram Main Channel'}</Pill>
                  </div>
                  <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-color)', margin: '0 0 4px 0' }}>{evt.title}</h3>
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: 0 }}>
                    {date.time ? date.full : evt.startsAt}
                  </p>
                </div>
              </Card>
            );
          })
        ) : (
          <Card style={{ padding: 16 }}>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              No upcoming events scheduled right now. Check back soon!
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
