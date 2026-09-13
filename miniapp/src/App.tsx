import React, { useState } from 'react';
import { useTelegram } from './hooks/useTelegram';
import { BottomNav } from './components/BottomNav';
import { HomeTab } from './components/tabs/HomeTab';
import { BibleTab } from './components/tabs/BibleTab';
import { QuizTab } from './components/tabs/QuizTab';
import { EventsTab } from './components/tabs/EventsTab';
import { CommunityTab } from './components/tabs/CommunityTab';
import { Card, Pill } from './components/ui';
import { RankBadge } from './components/RankBadge';
import { CommunityTicker } from './components/CommunityTicker';
import type { TabId } from './types/navigation';

const App: React.FC = () => {
  const { user, isInsideTelegram, verification, profile } = useTelegram();
  const [activeTab, setActiveTab] = useState<TabId>('home');
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [tabKey, setTabKey] = useState(0);

  const isVerified = verification.status === 'verified';
  const profileData = profile.status === 'ok' ? profile.profile : null;
  const displayName = user?.firstName || profileData?.displayName || 'Member';
  const initial = displayName[0]?.toUpperCase() || 'Y';

  const handleTabChange = (tab: TabId) => {
    if (tab === activeTab) return;
    setActiveTab(tab);
    setTabKey((k) => k + 1);
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'home':
        return <HomeTab user={user} profile={profile} verified={isVerified} onNavigate={handleTabChange} />;
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
    <div className="app-shell">
      <div style={{ position: 'sticky', top: 0, zIndex: 50 }}>
        <CommunityTicker />
      </div>

      <div className="app-frame">
        <header
          className="glass-panel"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 12,
            marginBottom: 16,
            padding: '12px 12px 12px 14px',
            borderRadius: 'var(--radius-xl)',
            position: 'sticky',
            top: 36,
            zIndex: 30,
          }}
        >
          <div style={{ minWidth: 0 }}>
            <div className="eyebrow" style={{ marginBottom: 3 }}>YOUTHOPIA BIBLE COMMUNITY</div>
            <h1 style={{ margin: 0, color: 'var(--text-color)', fontSize: 18, fontWeight: 900, lineHeight: 1.1 }}>
              Community Dashboard
            </h1>
            <p style={{ margin: '4px 0 0', color: 'var(--text-secondary)', fontSize: 12, fontWeight: 650 }}>
              Sharing God's Love All The Way
            </p>
          </div>

          <button
            aria-label="Open profile"
            onClick={() => setShowProfileModal(true)}
            style={{
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              minHeight: 44,
              maxWidth: 150,
              padding: '5px 8px 5px 5px',
              border: '1px solid rgba(221, 214, 254, 0.8)',
              borderRadius: 'var(--radius-full)',
              background: showProfileModal ? 'var(--primary-purple)' : 'rgba(255,255,255,0.92)',
              color: showProfileModal ? '#fff' : 'var(--text-color)',
              boxShadow: 'var(--shadow-xs)',
              cursor: 'pointer',
            }}
          >
            {user?.photoUrl ? (
              <img
                src={user.photoUrl}
                alt={displayName}
                width={34}
                height={34}
                style={{ borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--purple-200)' }}
              />
            ) : (
              <span
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: '50%',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'var(--grad-hero)',
                  color: '#fff',
                  fontSize: 14,
                  fontWeight: 900,
                }}
              >
                {initial}
              </span>
            )}
            <span style={{ minWidth: 0, textAlign: 'left' }}>
              <span style={{ display: 'block', fontSize: 11, fontWeight: 850, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {profileData ? `Level ${profileData.level}` : 'Profile'}
              </span>
              <span style={{ display: 'block', color: showProfileModal ? 'rgba(255,255,255,0.76)' : 'var(--text-muted)', fontSize: 10, fontWeight: 750 }}>
                {profileData ? `${profileData.totalXp.toLocaleString()} XP` : isVerified ? 'Verified' : 'Open'}
              </span>
            </span>
          </button>
        </header>

        {showProfileModal && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 1200,
              background: 'rgba(23, 17, 37, 0.34)',
              padding: 14,
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'center',
            }}
            onClick={() => setShowProfileModal(false)}
          >
            <Card
              style={{
                width: '100%',
                maxWidth: 500,
                padding: 18,
                borderRadius: '26px 26px 20px 20px',
                animation: 'fadeSlideIn 0.25s var(--ease) both',
              }}
              onClick={(event) => event.stopPropagation()}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 18 }}>
                <div>
                  <div className="eyebrow">Member Passport</div>
                  <h2 style={{ margin: '3px 0 0', fontSize: 22, lineHeight: 1.15 }}>{displayName}</h2>
                  {user?.username && <div style={{ marginTop: 3, color: 'var(--text-secondary)', fontSize: 13 }}>@{user.username}</div>}
                </div>
                <button
                  aria-label="Close profile"
                  onClick={() => setShowProfileModal(false)}
                  style={{
                    width: 34,
                    height: 34,
                    borderRadius: '50%',
                    border: '1px solid var(--slate-200)',
                    background: '#fff',
                    color: 'var(--text-secondary)',
                    fontSize: 18,
                    fontWeight: 800,
                    cursor: 'pointer',
                  }}
                >
                  x
                </button>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                {user?.photoUrl ? (
                  <img
                    src={user.photoUrl}
                    alt={displayName}
                    width={58}
                    height={58}
                    style={{ borderRadius: '50%', objectFit: 'cover', border: '3px solid var(--purple-200)' }}
                  />
                ) : (
                  <div
                    style={{
                      width: 58,
                      height: 58,
                      borderRadius: '50%',
                      background: 'var(--grad-hero)',
                      color: '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 900,
                      fontSize: 22,
                      boxShadow: 'var(--shadow-purple)',
                    }}
                  >
                    {initial}
                  </div>
                )}
                <div style={{ minWidth: 0 }}>
                  {profileData?.rankTitle && (
                    <RankBadge title={profileData.rankTitle} emoji={profileData.rankEmoji} color={profileData.rankBadgeColor} size="md" />
                  )}
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
                    <Pill color={isVerified ? 'success' : 'warning'}>{isVerified ? 'Server verified' : 'Identity pending'}</Pill>
                    <Pill color="purple">Trust {profileData?.trustScore ?? 100}/100</Pill>
                  </div>
                </div>
              </div>

              <div className="metric-grid" style={{ marginBottom: 16 }}>
                <div className="metric-tile">
                  <div className="metric-label">Level</div>
                  <div className="metric-value">{profileData?.level ?? 1}</div>
                </div>
                <div className="metric-tile">
                  <div className="metric-label">XP</div>
                  <div className="metric-value">{(profileData?.totalXp ?? 0).toLocaleString()}</div>
                </div>
                <div className="metric-tile">
                  <div className="metric-label">Accuracy</div>
                  <div className="metric-value">{profileData?.accuracyPct ?? 100}%</div>
                </div>
              </div>

              <div style={{ display: 'grid', gap: 9, color: 'var(--text-secondary)', fontSize: 13 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                  <span>Community tier</span>
                  <strong style={{ color: 'var(--text-color)', textTransform: 'capitalize' }}>{profileData?.engagementLevel ?? 'Active Member'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                  <span>Quizzes played</span>
                  <strong style={{ color: 'var(--text-color)' }}>{profileData?.quizzesPlayed ?? 0}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                  <span>Telegram launch</span>
                  <strong style={{ color: isInsideTelegram ? 'var(--success)' : 'var(--warning)' }}>
                    {isInsideTelegram ? 'Connected' : 'Dev mode'}
                  </strong>
                </div>
              </div>
            </Card>
          </div>
        )}

        <main key={tabKey} className="tab-enter">
          {renderActiveTab()}
        </main>

        <footer style={{ textAlign: 'center', marginTop: 28, paddingBottom: 16 }}>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', margin: 0, fontWeight: 600 }}>
            {isInsideTelegram ? 'Connected through Telegram' : 'Running outside Telegram (Dev Mode)'}
          </p>
          <p style={{ fontSize: 12, fontWeight: 750, color: 'var(--primary-purple)', margin: '6px 0 0 0', letterSpacing: '0.01em' }}>
            Powered by YouThopia Bible Community
          </p>
        </footer>
      </div>

      <BottomNav activeTab={activeTab} onTabChange={handleTabChange} />
    </div>
  );
};

export default App;
