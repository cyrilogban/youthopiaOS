import React, { useState } from 'react';
import { useTelegram } from './hooks/useTelegram';
import { BottomNav } from './components/BottomNav';
import { HomeTab } from './components/tabs/HomeTab';
import { BibleTab } from './components/tabs/BibleTab';
import { QuizTab } from './components/tabs/QuizTab';
import { EventsTab } from './components/tabs/EventsTab';
import { CommunityTab } from './components/tabs/CommunityTab';
import { Card } from './components/ui';
import type { TabId } from './types/navigation';

const App: React.FC = () => {
  const { user, isInsideTelegram, verification, profile } = useTelegram();
  const [activeTab, setActiveTab] = useState<TabId>('home');
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [tabKey, setTabKey] = useState(0);

  const isVerified = verification.status === 'verified';
  const profileData = profile.status === 'ok' ? profile.profile : null;

  // Re-trigger the entrance animation whenever the tab changes.
  const handleTabChange = (tab: TabId) => {
    if (tab === activeTab) return;
    setActiveTab(tab);
    setTabKey((k) => k + 1);
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'home':
        return <HomeTab user={user} profile={profile} verified={isVerified} />;
      case 'bible':
        return <BibleTab />;
      case 'quiz':
        return <QuizTab profile={profile} />;
      case 'events':
        return <EventsTab />;
      case 'community':
        return <CommunityTab />;
    }
  };

  return (
    <div
      className="app-enter"
      style={{
        padding: '20px 16px 84px 16px',
        maxWidth: '480px',
        margin: '0 auto',
        minHeight: '100vh',
        backgroundColor: 'var(--bg-color)',
      }}
    >
      {/* Top Header */}
      <header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          paddingBottom: '12px',
          borderBottom: '1px solid var(--slate-200)',
        }}
      >
        <div>
          <h1
            style={{
              color: 'var(--primary-purple)',
              fontSize: 16,
              fontWeight: 800,
              margin: 0,
              letterSpacing: '-0.01em',
              textTransform: 'uppercase',
            }}
          >
            YOUTHOPIA BIBLE COMMUNITY
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 11, margin: '2px 0 0 0', fontWeight: 500 }}>
            Sharing God&apos;s Love All The Way
          </p>
        </div>

        {/* Member Profile Button (Always Visible) */}
        <button
          onClick={() => setShowProfileModal(!showProfileModal)}
          style={{
            background: showProfileModal ? 'var(--primary-purple)' : 'var(--surface)',
            color: showProfileModal ? '#ffffff' : 'var(--text-color)',
            border: '1px solid var(--slate-200)',
            borderRadius: 'var(--radius-full)',
            padding: '5px 12px',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: 11,
            boxShadow: 'var(--shadow-xs)',
            transition: 'all 0.15s var(--ease)',
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              backgroundColor: isVerified ? 'var(--success)' : 'var(--warning)',
            }}
          />
          <span>{profileData ? `Lvl ${profileData.level} • ${profileData.totalXp} XP` : 'Profile'}</span>
        </button>
      </header>

      {/* Member Profile Modal Overlay (Always toggleable) */}
      {showProfileModal && (
        <Card style={{ padding: 18, marginBottom: 16, animation: 'fadeSlideIn 0.25s var(--ease) both' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <span
              style={{
                fontSize: 12,
                fontWeight: 700,
                color: 'var(--primary-purple)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Member Identity & Profile
            </span>
            <button
              onClick={() => setShowProfileModal(false)}
              style={{
                background: 'var(--slate-100)',
                border: 'none',
                width: 28,
                height: 28,
                borderRadius: '50%',
                fontSize: 14,
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'background 0.15s var(--ease)',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--slate-200)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--slate-100)')}
            >
              ✕
            </button>
          </div>

          {/* User Info Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              marginBottom: 14,
              paddingBottom: 12,
              borderBottom: '1px solid var(--slate-100)',
            }}
          >
            {user?.photoUrl ? (
              <img
                src={user.photoUrl}
                alt={user.firstName}
                width={40}
                height={40}
                style={{ borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--purple-200)' }}
              />
            ) : (
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  background: 'var(--grad-hero)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: 16,
                }}
              >
                {user?.firstName?.[0]?.toUpperCase() || 'G'}
              </div>
            )}
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-color)' }}>
                {user ? `${user.firstName}${user.lastName ? ` ${user.lastName}` : ''}` : 'Guest Member'}
              </div>
              {user?.username && <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>@{user.username}</div>}
            </div>
          </div>

          {/* Level & XP Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
            <div
              style={{ background: 'var(--surface-soft)', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--slate-100)' }}
            >
              <div style={{ fontSize: 10, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Level Rank</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--primary-purple)', marginTop: 2 }}>
                Level {profileData ? profileData.level : 1}
              </div>
            </div>
            <div
              style={{ background: 'var(--surface-soft)', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--slate-100)' }}
            >
              <div style={{ fontSize: 10, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Earned</div>
              <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-color)', marginTop: 2 }}>
                {profileData ? `${profileData.totalXp} XP` : '0 XP'}
              </div>
            </div>
          </div>

          {/* Status Meta */}
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
              <span>Identity Verification:</span>
              <span style={{ fontWeight: 600, color: 'var(--success)' }}>
                {isVerified ? 'Verified Server-Side' : 'Member Identity Active'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginTop: 8 }}>
              <span>Community Tier:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-color)', textTransform: 'capitalize' }}>
                {profileData ? profileData.engagementLevel : 'Active Member'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginTop: 8 }}>
              <span>Pete Security Shield:</span>
              <span style={{ fontWeight: 700, color: 'var(--success)' }}>
                Trust Score: {profileData?.trustScore ?? 100} / 100 &bull; Safe
              </span>
            </div>
          </div>
        </Card>
      )}

      {/* Main Active Tab Content */}
      <main key={tabKey} className="tab-enter">
        {renderActiveTab()}
      </main>

      {/* Bottom Navigation */}
      <BottomNav activeTab={activeTab} onTabChange={handleTabChange} />

      {/* Footer Meta */}
      <footer style={{ textAlign: 'center', marginTop: 28 }}>
        <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0 }}>
          {isInsideTelegram ? 'Connected through Telegram' : 'Running outside Telegram (Dev Mode)'}
        </p>
        <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--primary-purple)', marginTop: 6 }}>
          Powered by YouThopia Bible Community
        </p>
      </footer>
    </div>
  );
};

export default App;
