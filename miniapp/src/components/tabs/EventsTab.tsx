import React, { useEffect, useState } from 'react';
import { fetchEvents, type EventItem } from '../../services/api';

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

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 4px 0', color: '#0f172a' }}>
          Events & Schedule
        </h2>
        <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
          Powered by Eddy Bot &bull; Community Calendar & Reminders
        </p>
      </div>

      {/* Upcoming Events List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {loading ? (
          <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '16px', fontSize: '12px', color: '#64748b' }}>
            Loading community schedule from Supabase…
          </div>
        ) : (
          events.map((evt, idx) => (
            <div
              key={idx}
              style={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '14px',
                padding: '16px',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: '#6d28d9', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {evt.category || 'Community Gathering'}
                </span>
                <span style={{ fontSize: '11px', color: '#64748b', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '4px' }}>
                  {evt.location || 'Telegram Main Channel'}
                </span>
              </div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', margin: '0 0 4px 0' }}>
                {evt.title}
              </h3>
              <p style={{ fontSize: '12px', color: '#475569', margin: 0 }}>
                {evt.startsAt}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
