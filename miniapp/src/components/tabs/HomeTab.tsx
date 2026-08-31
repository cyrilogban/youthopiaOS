import React, { useEffect, useState } from 'react';
import type { TelegramUser } from '../../types/telegram';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchVotd, type VotdItem } from '../../services/api';
import { Card, Skeleton } from '../ui';

interface HomeTabProps {
  user: TelegramUser | null;
  profile: ProfileState;
  verified: boolean;
}

export const HomeTab: React.FC<HomeTabProps> = ({ user, profile, verified }) => {
  const profileData = profile.status === 'ok' ? profile.profile : null;
  const [votd, setVotd] = useState<VotdItem | null>(null);
  const [loadingVotd, setLoadingVotd] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const item = await fetchVotd('KJV');
      if (!cancelled) {
        setVotd(item);
        setLoadingVotd(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const initial = user?.firstName?.[0]?.toUpperCase() || 'G';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Gradient Greeting Hero */}
      <div
        style={{
          background: 'var(--grad-hero)',
          borderRadius: 'var(--radius-xl)',
          padding: '22px 20px',
          color: '#ffffff',
          boxShadow: '0 10px 28px rgba(109, 40, 217, 0.28)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: -50,
            right: -40,
            width: 160,
            height: 160,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.08)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: -60,
            left: 30,
            width: 120,
            height: 120,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.06)',
          }}
        />

        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 14 }}>
          {user?.photoUrl ? (
            <img
              src={user.photoUrl}
              alt={user.firstName}
              width={52}
              height={52}
              style={{
                borderRadius: '50%',
                objectFit: 'cover',
                border: '2px solid rgba(255,255,255,0.5)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              }}
            />
          ) : (
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: '50%',
                background: 'rgba(255,255,255,0.22)',
                border: '2px solid rgba(255,255,255,0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: 22,
              }}
            >
              {initial}
            </div>
          )}
          <div>
            <div style={{ fontSize: 20, fontWeight: 800, lineHeight: 1.2 }}>
              Welcome back{user ? `, ${user.firstName}` : ''}
            </div>
            <div style={{ fontSize: 13, opacity: 0.9, marginTop: 2 }}>
              {user?.username ? `@${user.username}` : 'Sharing God\'s Love All The Way'}
            </div>
          </div>
        </div>

        <div
          style={{
            position: 'relative',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 7,
            marginTop: 16,
            background: 'rgba(255,255,255,0.16)',
            border: '1px solid rgba(255,255,255,0.25)',
            borderRadius: 'var(--radius-full)',
            padding: '5px 12px',
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#4ade80', boxShadow: '0 0 0 3px rgba(74,222,128,0.25)' }} />
          {verified ? 'Verified Member' : 'Member Identity Active'}
        </div>
      </div>

      {/* Quick Profile Summary Bar */}
      {profileData && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <Card hover style={{ padding: 14 }}>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Current Level
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--primary-purple)', marginTop: 4 }}>Level {profileData.level}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>{profileData.engagementLevel} tier</div>
          </Card>
          <Card hover style={{ padding: 14 }}>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Community XP
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--primary-purple)', marginTop: 4 }}>
              {profileData.totalXp.toLocaleString()} XP
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>All-time earnings</div>
          </Card>
        </div>
      )}

      {/* Dynamic Verse of the Day Card Preview */}
      <Card style={{ padding: 18 }} hover>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              color: 'var(--primary-purple)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            Verse of the Day
          </span>
          <span
            style={{
              fontSize: 11,
              color: 'var(--primary-purple)',
              background: 'var(--purple-50)',
              border: '1px solid var(--purple-200)',
              padding: '2px 8px',
              borderRadius: 'var(--radius-full)',
              fontWeight: 600,
            }}
          >
            {votd?.translation || 'KJV'}
          </span>
        </div>

        {loadingVotd ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <Skeleton height={14} />
            <Skeleton height={14} width="90%" />
            <Skeleton height={12} width="40%" style={{ alignSelf: 'flex-end', marginTop: 6 }} />
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: 12 }}>
              <div
                style={{
                  width: 4,
                  alignSelf: 'stretch',
                  borderRadius: 2,
                  background: 'var(--grad-hero)',
                  flexShrink: 0,
                }}
              />
              <p style={{ fontSize: 15, color: 'var(--slate-700)', lineHeight: 1.65, fontStyle: 'italic', margin: 0 }}>
                &ldquo;{votd?.text}&rdquo;
              </p>
            </div>
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--primary-purple)', textAlign: 'right', marginTop: 10 }}>
              {votd?.reference}
            </div>
          </>
        )}
      </Card>
    </div>
  );
};
