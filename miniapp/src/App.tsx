import React, { useState } from 'react';
import { useTelegram } from './hooks/useTelegram';
import { BottomNav } from './components/BottomNav';
import { HomeTab } from './components/tabs/HomeTab';
import { BibleTab } from './components/tabs/BibleTab';
import { QuizTab } from './components/tabs/QuizTab';
import { EventsTab } from './components/tabs/EventsTab';
import { CommunityTab } from './components/tabs/CommunityTab';
import type { TabId } from './types/navigation';

const App: React.FC = () => {
  const { user, isInsideTelegram, verification, profile } = useTelegram();
  const [activeTab, setActiveTab] = useState<TabId>('home');
  const [showProfileModal, setShowProfileModal] = useState(false);

  const isVerified = verification.status === 'verified';
  const profileData = profile.status === 'ok' ? profile.profile : null;

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
      style={{
        padding: '20px 16px 84px 16px',
        maxWidth: '480px',
        margin: '0 auto',
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        boxSizing: 'border-box',
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
          borderBottom: '1px solid #e2e8f0',
        }}
      >
        <div>
          <h1 style={{ color: '#6d28d9', fontSize: '20px', fontWeight: 800, margin: 0, letterSpacing: '-0.02em' }}>
            YouThopiaOS
          </h1>
          <p style={{ color: '#64748b', fontSize: '11px', margin: '2px 0 0 0', fontWeight: 500 }}>
            Christian Community Operating System
          </p>
        </div>

        {/* Member Profile Button (Always Visible) */}
        <button
          onClick={() => setShowProfileModal(!showProfileModal)}
          style={{
            background: showProfileModal ? '#6d28d9' : '#ffffff',
            color: showProfileModal ? '#ffffff' : '#0f172a',
            border: '1px solid #e2e8f0',
            borderRadius: '20px',
            padding: '5px 12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '11px',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)',
            transition: 'all 0.15s ease',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: isVerified ? '#16a34a' : '#d97706',
            }}
          />
          <span>{profileData ? `Lvl ${profileData.level} • ${profileData.totalXp} XP` : 'Profile'}</span>
        </button>
      </header>

      {/* Member Profile Modal Overlay (Always toggleable) */}
      {showProfileModal && (
        <div
          style={{
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '14px',
            padding: '18px',
            marginBottom: '16px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.06)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#6d28d9', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Member Identity & Profile
              </span>
            </div>
            <button
              onClick={() => setShowProfileModal(false)}
              style={{ background: 'none', border: 'none', fontSize: '14px', color: '#64748b', cursor: 'pointer', fontWeight: 700 }}
            >
              ✕
            </button>
          </div>

          {/* User Info Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px', paddingBottom: '12px', borderBottom: '1px solid #f1f5f9' }}>
            {user?.photoUrl && (
              <img
                src={user.photoUrl}
                alt={user.firstName}
                width={40}
                height={40}
                style={{ borderRadius: '50%', objectFit: 'cover' }}
              />
            )}
            <div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a' }}>
                {user ? `${user.firstName}${user.lastName ? ` ${user.lastName}` : ''}` : 'Guest Member'}
              </div>
              {user?.username && (
                <div style={{ fontSize: '12px', color: '#64748b' }}>@{user.username}</div>
              )}
            </div>
          </div>

          {/* Level & XP Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '14px' }}>
            <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '10px', border: '1px solid #f1f5f9' }}>
              <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Level Rank</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#6d28d9', marginTop: '2px' }}>
                Level {profileData ? profileData.level : 1}
              </div>
            </div>
            <div style={{ backgroundColor: '#f8fafc', padding: '10px 12px', borderRadius: '10px', border: '1px solid #f1f5f9' }}>
              <div style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Earned</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>
                {profileData ? `${profileData.totalXp} XP` : '0 XP'}
              </div>
            </div>
          </div>

          {/* Status Meta */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#64748b' }}>
            <span>Identity Verification:</span>
            <span style={{ fontWeight: 600, color: '#15803d' }}>
              {isVerified ? 'Verified Server-Side' : 'Member Identity Active'}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#64748b', marginTop: '6px' }}>
            <span>Community Tier:</span>
            <span style={{ fontWeight: 600, color: '#0f172a', textTransform: 'capitalize' }}>
              {profileData ? profileData.engagementLevel : 'Active Member'}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#64748b', marginTop: '6px' }}>
            <span>Pete Security Shield:</span>
            <span style={{ fontWeight: 700, color: '#16a34a' }}>
              Trust Score: {profileData?.trustScore ?? 100} / 100 &bull; Safe
            </span>
          </div>
        </div>
      )}

      {/* Main Active Tab Content */}
      <main>{renderActiveTab()}</main>

      {/* Bottom Navigation */}
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Footer Meta */}
      <footer style={{ textAlign: 'center', marginTop: '24px' }}>
        <p style={{ fontSize: '11px', color: '#94a3b8', margin: 0 }}>
          {isInsideTelegram ? 'Connected through Telegram' : 'Running outside Telegram (Dev Mode)'}
        </p>
        <p style={{ fontSize: '10px', color: '#cbd5e1', marginTop: '4px', margin: 0 }}>
          Powered by YouThopia Bible Community
        </p>
      </footer>
    </div>
  );
};

export default App;
