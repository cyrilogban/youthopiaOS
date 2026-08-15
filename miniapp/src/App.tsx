import React from 'react';
import { useTelegram } from './hooks/useTelegram';

const App: React.FC = () => {
  const { user, isInsideTelegram } = useTelegram();

  return (
    <div style={{ padding: '20px', maxWidth: '480px', margin: '0 auto' }}>
      <header style={{ textAlign: 'center', marginBottom: '24px' }}>
        <h1 style={{ color: 'var(--primary-purple)', fontSize: '24px', margin: '0 0 8px 0' }}>
          YouThopiaOS
        </h1>
        <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>
          Christian Community Operating System
        </p>
      </header>

      <div
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--card-border)',
          borderRadius: '16px',
          padding: '20px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        }}
      >
        {user ? (
          <>
            <div
              style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}
            >
              {user.photoUrl && (
                <img
                  src={user.photoUrl}
                  alt={user.firstName}
                  width={48}
                  height={48}
                  style={{ borderRadius: '50%', objectFit: 'cover' }}
                />
              )}
              <div>
                <h2 style={{ fontSize: '18px', margin: 0 }}>
                  👋 Welcome, {user.firstName}
                  {user.lastName ? ` ${user.lastName}` : ''}
                </h2>
                {user.username && (
                  <p style={{ fontSize: '13px', color: '#64748b', margin: '2px 0 0 0' }}>
                    @{user.username}
                  </p>
                )}
              </div>
            </div>
            <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6', margin: 0 }}>
              You&apos;re signed in to YOUTHOPIA BIBLE COMMUNITY
              {user.isPremium ? ' — thanks for being a Telegram Premium member! ⭐' : '.'}
            </p>
          </>
        ) : (
          <>
            <h2 style={{ fontSize: '18px', margin: '0 0 12px 0' }}>👋 Welcome to YouThopiaOS</h2>
            <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6', margin: 0 }}>
              Open this app inside Telegram to sign in and see your profile.
            </p>
          </>
        )}
      </div>

      <p style={{ textAlign: 'center', fontSize: '12px', color: '#94a3b8', marginTop: '16px' }}>
        {isInsideTelegram
          ? '🟢 Connected to Telegram'
          : '⚪ Running outside Telegram (dev preview)'}
      </p>
    </div>
  );
};

export default App;
