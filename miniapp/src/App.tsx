import React, { useEffect, useState } from 'react';
import { useTelegram } from './hooks/useTelegram';
import { BottomNav } from './components/BottomNav';
import { HomeTab } from './components/tabs/HomeTab';
import { BibleTab } from './components/tabs/BibleTab';
import { QuizTab } from './components/tabs/QuizTab';
import { EventsTab } from './components/tabs/EventsTab';
import { CommunityTab } from './components/tabs/CommunityTab';
import { Card, Pill } from './components/ui';
import { RankBadge } from './components/RankBadge';
import { TourOverlay, markTourAsSeen } from './components/TourOverlay';
import { fetchCommunityTour, type Tour } from './services/api';
import { getRawInitData } from './services/telegram';
import type { TabId } from './types/navigation';

const App: React.FC = () => {
  const { user, isInsideTelegram, verification, profile, refreshProfile } = useTelegram();
  const [activeTab, setActiveTab] = useState<TabId>('home');
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [tabKey, setTabKey] = useState(0);
  const [tour, setTour] = useState<Tour | null>(null);
  const [tourOpen, setTourOpen] = useState(false);

  const profileData = profile.status === 'ok' ? profile.profile : null;
  const isVerified = verification.status === 'verified';
  const totalXp = profileData?.totalXp ?? 0;
  const computedLevel = Math.max(1, Math.floor(totalXp / 100) + 1);
  const level = profileData?.level && profileData.level > 1 ? profileData.level : computedLevel;
  const displayName = user?.firstName || profileData?.displayName || 'Member';
  const initial = displayName[0]?.toUpperCase() || 'Y';

  // Load the shared tour copy once (same content the 5 Telegram bots serve).
  useEffect(() => {
    let cancelled = false;
    void fetchCommunityTour().then((loaded) => {
      if (!cancelled && loaded) setTour(loaded);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  // First-launch auto-open: only for verified members who never finished
  // orientation, and only once per device.
  useEffect(() => {
    if (profile.status !== 'ok') return;
    if (profile.profile.engagementLevel === 'onboarded') {
      markTourAsSeen();
      return;
    }
    let seen = false;
    try {
      seen = window.localStorage.getItem('youthopia_tour_seen_v1') === '1';
    } catch {
      seen = true;
    }
    if (!seen) setTourOpen(true);
  }, [profile]);

  const openTour = () => setTourOpen(true);
  const closeTour = () => {
    markTourAsSeen();
    setTourOpen(false);
  };

  const handleTabChange = (tab: TabId) => {
    if (tab === activeTab) return;
    setActiveTab(tab);
    setTabKey((current) => current + 1);
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
        return <CommunityTab onOpenTour={openTour} />;
    }
  };

  return (
    <div className="app-shell">
      <div className="app-frame">
        <header className="app-header">
          <div>
            <div className="brand-kicker">YouThopia Bible Community</div>
            <div className="brand-name">Sharing God's Love All The Way</div>
          </div>

          <button className="profile-trigger" onClick={() => setShowProfileModal(true)} aria-label="Open your profile">
            <span className="profile-avatar">
              {user?.photoUrl ? <img src={user.photoUrl} alt={displayName} /> : initial}
            </span>
            <span className="profile-trigger-copy">
              <strong>Level {level}</strong>
              <span>{totalXp.toLocaleString()} XP</span>
            </span>
          </button>
        </header>

        <main key={tabKey} className="tab-enter">
          {renderActiveTab()}
        </main>

        <footer style={{ marginTop: 28, color: 'var(--text-muted)', fontSize: 11, textAlign: 'center' }}>
          {isInsideTelegram ? 'Connected through Telegram' : 'Preview mode'}
        </footer>
      </div>

      <BottomNav activeTab={activeTab} onTabChange={handleTabChange} />

      {tourOpen && (
        <TourOverlay
          tour={tour}
          canEarnXp={isVerified && profileData?.engagementLevel !== 'onboarded'}
          rawInitData={getRawInitData()}
          onClose={closeTour}
          onFinish={() => void refreshProfile()}
        />
      )}

      {showProfileModal && (
        <div
          onClick={() => setShowProfileModal(false)}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1100,
            display: 'flex',
            alignItems: 'flex-end',
            padding: 12,
            background: 'rgba(31, 23, 43, 0.36)',
          }}
        >
          <Card
            onClick={(event) => event.stopPropagation()}
            style={{ width: '100%', maxWidth: 496, margin: '0 auto', padding: 20, borderRadius: '24px 24px 18px 18px' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start' }}>
              <div>
                <div className="eyebrow">Growth passport</div>
                <h2 style={{ margin: '4px 0 0', fontSize: 24 }}>{displayName}</h2>
                {user?.username && <p className="muted-copy" style={{ marginTop: 3 }}>@{user.username}</p>}
              </div>
              <button
                onClick={() => setShowProfileModal(false)}
                aria-label="Close profile"
                style={{ width: 36, height: 36, border: '1px solid var(--slate-200)', borderRadius: '50%', background: '#fff', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                Close
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 20 }}>
              <span className="profile-avatar" style={{ width: 58, height: 58, fontSize: 20 }}>
                {user?.photoUrl ? <img src={user.photoUrl} alt={displayName} /> : initial}
              </span>
              <div style={{ display: 'grid', gap: 8 }}>
                {profileData?.rankTitle && <RankBadge title={profileData.rankTitle} emoji={profileData.rankEmoji} color={profileData.rankBadgeColor} size="md" />}
                <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
                  <Pill color={isVerified ? 'success' : 'warning'}>{isVerified ? 'Verified member' : 'Identity pending'}</Pill>
                  <Pill color="purple">Trust {profileData?.trustScore ?? 100}</Pill>
                </div>
              </div>
            </div>

            <div className="metric-grid" style={{ marginTop: 20 }}>
              <div className="metric-tile"><div className="metric-label">Level</div><div className="metric-value">{level}</div></div>
              <div className="metric-tile"><div className="metric-label">XP</div><div className="metric-value">{totalXp.toLocaleString()}</div></div>
              <div className="metric-tile"><div className="metric-label">Accuracy</div><div className="metric-value">{profileData?.accuracyPct ?? 100}%</div></div>
            </div>

            <div style={{ display: 'grid', gap: 10, marginTop: 20, color: 'var(--text-secondary)', fontSize: 13 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}><span>Community tier</span><strong style={{ color: 'var(--ink)', textTransform: 'capitalize' }}>{profileData?.engagementLevel ?? 'Member'}</strong></div>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}><span>Quizzes played</span><strong style={{ color: 'var(--ink)' }}>{profileData?.quizzesPlayed ?? 0}</strong></div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default App;
