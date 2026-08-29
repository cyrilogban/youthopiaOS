import React, { useEffect, useState } from 'react';
import type { TelegramUser } from '../../types/telegram';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchVotd, type VotdItem } from '../../services/api';

interface HomeTabProps {
  user: TelegramUser | null;
  profile: ProfileState;
  verified: boolean;
}

export const HomeTab: React.FC<HomeTabProps> = ({ user, profile, verified }) => {
  const profileData = profile.status === 'ok' ? profile.profile : null;
  const [votd, setVotd] = useState<VotdItem | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const item = await fetchVotd('KJV');
      if (!cancelled) {
        setVotd(item);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* User Greeting & Status Banner */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '14px',
          padding: '18px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
          {user?.photoUrl && (
            <img
              src={user.photoUrl}
              alt={user.firstName}
              width={44}
              height={44}
              style={{ borderRadius: '50%', objectFit: 'cover', border: '1px solid #cbd5e1' }}
            />
          )}
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 700, margin: 0, color: '#0f172a' }}>
              Welcome back{user ? `, ${user.firstName}` : ''}
            </h2>
            {user?.username && (
              <p style={{ fontSize: '13px', color: '#64748b', margin: '2px 0 0 0' }}>
                @{user.username}
              </p>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px' }}>
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#16a34a',
            }}
          />
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#15803d' }}>
            {verified ? 'Cryptographically Verified Member' : 'Member Identity Active'}
          </span>
        </div>
      </div>

      {/* Quick Profile Summary Bar */}
      {profileData && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
          }}
        >
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '14px',
            }}
          >
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Current Level
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: '#6d28d9', marginTop: '4px' }}>
              Level {profileData.level}
            </div>
          </div>
          <div
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '14px',
            }}
          >
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Community XP
            </div>
            <div style={{ fontSize: '24px', fontWeight: 700, color: '#6d28d9', marginTop: '4px' }}>
              {profileData.totalXp.toLocaleString()} XP
            </div>
          </div>
        </div>
      )}

      {/* Dynamic Verse of the Day Card Preview */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '14px',
          padding: '18px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#6d28d9', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Verse of the Day
          </span>
          <span style={{ fontSize: '11px', color: '#64748b', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
            {votd?.translation || 'KJV'}
          </span>
        </div>
        <p style={{ fontSize: '14px', color: '#334155', lineHeight: '1.6', fontStyle: 'italic', margin: '0 0 10px 0' }}>
          &ldquo;{votd?.text || 'Loading today’s active Scripture…'}&rdquo;
        </p>
        <div style={{ fontSize: '12px', fontWeight: 600, color: '#475569', textAlign: 'right' }}>
          {votd?.reference || 'Jeremiah 29:11'}
        </div>
      </div>
    </div>
  );
};
