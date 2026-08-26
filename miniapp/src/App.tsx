import React from 'react';
import { useTelegram, type ProfileState } from './hooks/useTelegram';
import type { TelegramUser } from './types/telegram';

/** The signed-in greeting, reused for the server-verified and client-only states. */
const Greeting: React.FC<{ user: TelegramUser; verified: boolean }> = ({ user, verified }) => (
  <>
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
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
    <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6', margin: '0 0 12px 0' }}>
      You&apos;re signed in to YouThopiaOS
      {user.isPremium ? ' — thanks for being a Telegram Premium member! ⭐' : '.'}
    </p>
    {verified ? (
      <p style={{ fontSize: '13px', color: '#16a34a', margin: 0, fontWeight: 600 }}>
        🟢 Verified by the server
      </p>
    ) : (
      <p style={{ fontSize: '13px', color: '#d97706', margin: 0, fontWeight: 600 }}>
        ⚠️ Signed in locally — not verified by the server
      </p>
    )}
  </>
);

/** The YouThopiaOS profile (XP, level, membership) shown beneath a server-verified greeting. */
const ProfileDetails: React.FC<{ profile: ProfileState }> = ({ profile }) => {
  switch (profile.status) {
    case 'idle':
      return null; // verification hasn't succeeded yet — nothing of ours to show
    case 'loading':
      return (
        <p style={{ fontSize: '13px', color: '#64748b', margin: '12px 0 0 0' }}>
          Loading your profile…
        </p>
      );
    case 'ok': {
      const p = profile.profile;
      return (
        <div style={{ marginTop: '14px', paddingTop: '14px', borderTop: '1px solid var(--card-border)' }}>
          <div style={{ display: 'flex', gap: '24px' }}>
            <div>
              <div style={{ fontSize: '22px', fontWeight: 700, color: 'var(--primary-purple)' }}>
                {p.level}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Level</div>
            </div>
            <div>
              <div style={{ fontSize: '22px', fontWeight: 700, color: 'var(--primary-purple)' }}>
                {p.totalXp}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Total XP</div>
            </div>
          </div>
          <p style={{ fontSize: '12px', color: '#64748b', margin: '10px 0 0 0' }}>
            Membership: {p.engagementLevel}
          </p>
        </div>
      );
    }
    case 'none':
      return (
        <p style={{ fontSize: '13px', color: '#64748b', margin: '12px 0 0 0' }}>
          You don&apos;t have a YouThopiaOS profile yet.
        </p>
      );
    case 'unverified':
      return null; // only rendered under the verified branch — a defensive no-op
    case 'error':
      return (
        <p style={{ fontSize: '13px', color: '#dc2626', margin: '12px 0 0 0' }}>
          Couldn&apos;t load your profile: {profile.message}
        </p>
      );
  }
};

const App: React.FC = () => {
  const { user, isInsideTelegram, verification, profile } = useTelegram();

  // One exhaustive switch over the single verification state (TS errors if a
  // case is missed). 'display' here is not 'trust': the client-claimed user is
  // only ever shown labeled 'not verified'; real trust is the 'verified' case.
  const renderCard = () => {
    switch (verification.status) {
      case 'loading':
        return (
          <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6', margin: 0 }}>
            Verifying your identity…
          </p>
        );
      case 'verified':
        return (
          <>
            <Greeting user={verification.user} verified />
            <ProfileDetails profile={profile} />
          </>
        );
      case 'unverified':
        return user ? (
          <Greeting user={user} verified={false} />
        ) : (
          <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6', margin: 0 }}>
            Signed in, but the server couldn&apos;t verify you.
          </p>
        );
      case 'no-telegram':
        return (
          <>
            <h2 style={{ fontSize: '18px', margin: '0 0 12px 0' }}>👋 Welcome to YouThopiaOS</h2>
            <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6', margin: 0 }}>
              Open this app inside Telegram to sign in and see your profile.
            </p>
          </>
        );
      case 'error':
        return (
          <p style={{ fontSize: '14px', color: '#dc2626', lineHeight: '1.6', margin: 0 }}>
            ⚠️ Couldn&apos;t reach the server: {verification.message}
          </p>
        );
    }
  };

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
        {renderCard()}
      </div>

      <p style={{ textAlign: 'center', fontSize: '12px', color: '#94a3b8', marginTop: '16px' }}>
        {isInsideTelegram
          ? '🟢 Connected through Telegram'
          : '⚪ Running outside Telegram (dev preview)'}
      </p>
      <p style={{ textAlign: 'center', fontSize: '11px', color: '#cbd5e1', marginTop: '6px' }}>
        Powered by YouThopia Bible Community
      </p>
    </div>
  );
};

export default App;
