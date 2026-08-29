import React from 'react';

export const EventsTab: React.FC = () => {
  const events = [
    {
      title: 'Weekly Bible Study & Discussion',
      time: 'Sundays at 6:00 PM UTC',
      category: 'Community Gathering',
      location: 'Telegram Main Channel',
    },
    {
      title: 'Midweek Prayer & Intercession',
      time: 'Wednesdays at 7:30 PM UTC',
      category: 'Prayer Session',
      location: 'Voice Chat Room',
    },
    {
      title: 'Weekend Scripture Challenge',
      time: 'Saturdays at 4:00 PM UTC',
      category: 'Community Quiz',
      location: 'Lusy Bot Channel',
    },
  ];

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
        {events.map((evt, idx) => (
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
                {evt.category}
              </span>
              <span style={{ fontSize: '11px', color: '#64748b', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '4px' }}>
                {evt.location}
              </span>
            </div>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', margin: '0 0 4px 0' }}>
              {evt.title}
            </h3>
            <p style={{ fontSize: '12px', color: '#475569', margin: 0 }}>
              {evt.time}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
