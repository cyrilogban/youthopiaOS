import React, { useEffect, useState } from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { useTelegram } from './hooks/useTelegram';
import { AppDataProvider } from './context/AppData';
import { BottomNav } from './components/BottomNav';
import { TourOverlay, markTourAsSeen } from './components/TourOverlay';
import { fetchCommunityTour, type Tour } from './services/api';
import { getRawInitData } from './services/telegram';
import { HomeRoute } from './routes/HomeRoute';
import { TheoRoute } from './routes/theo/TheoRoute';
import { LusieRoute } from './routes/lusie/LusieRoute';
import { EdieRoute } from './routes/edie/EdieRoute';
import { SusieRoute } from './routes/susie/SusieRoute';
import { PeteRoute } from './routes/pete/PeteRoute';
import { pathForTab, tabForPath, type TabId } from './types/navigation';

const BOT_PATHS = ['/theo', '/lusie', '/edie', '/susie', '/pete'];

const App: React.FC = () => {
  const telegram = useTelegram();
  const { user, isInsideTelegram, verification, profile, refreshProfile } = telegram;
  const location = useLocation();
  const navigate = useNavigate();
  const [tour, setTour] = useState<Tour | null>(null);
  const [tourOpen, setTourOpen] = useState(false);

  const profileData = profile.status === 'ok' ? profile.profile : null;
  const isVerified = verification.status === 'verified';
  const totalXp = profileData?.totalXp ?? 0;
  const computedLevel = Math.max(1, Math.floor(totalXp / 100) + 1);
  const level = profileData?.level && profileData.level > 1 ? profileData.level : computedLevel;
  const displayName = user?.firstName || profileData?.displayName || 'Member';
  const initial = displayName[0]?.toUpperCase() || 'Y';
  const activeTab = tabForPath(location.pathname);

  const isBotRoute = BOT_PATHS.some((path) => location.pathname === path || location.pathname.startsWith(`${path}/`));
  const botMatch = location.pathname.match(/^\/(theo|lusie|edie|susie|pete)(?:\/|$)/);
  const profilePath = botMatch ? `/${botMatch[1]}/profile` : '/theo/profile';


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
    const nextPath = pathForTab(tab);
    if (nextPath !== location.pathname) navigate(nextPath);
  };

  return (
    <AppDataProvider value={telegram}>
      <div className="app-shell">
        <div className="app-frame" style={{ paddingBottom: isBotRoute ? 96 : undefined }}>
          <header className="app-header">
            <div>
              <div className="brand-kicker">YouThopia Bible Community</div>
              <div className="brand-name">Sharing God's Love All The Way</div>
            </div>

            <button className="profile-trigger" onClick={() => navigate(profilePath)} aria-label="Open your profile">
              <span className="profile-avatar">
                {user?.photoUrl ? <img src={user.photoUrl} alt={displayName} /> : initial}
              </span>
              <span className="profile-trigger-copy">
                <strong>Level {level}</strong>
                <span>{totalXp.toLocaleString()} XP</span>
              </span>
            </button>
          </header>

          <main key={location.pathname} className="tab-enter">
            <Routes>
              <Route path="/" element={<Navigate to="/home" replace />} />
              <Route
                path="/home"
                element={<HomeRoute user={user} profile={profile} verified={isVerified} onNavigate={handleTabChange} />}
              />
              <Route path="/theo/*" element={<TheoRoute />} />
              <Route path="/lusie/*" element={<LusieRoute />} />
              <Route path="/edie/*" element={<EdieRoute />} />
              <Route path="/susie/*" element={<SusieRoute onOpenTour={openTour} />} />
              <Route path="/pete/*" element={<PeteRoute />} />
              <Route path="*" element={<Navigate to="/home" replace />} />
            </Routes>
          </main>

          <footer style={{ marginTop: 28, color: 'var(--text-muted)', fontSize: 11, textAlign: 'center' }}>
            {isInsideTelegram ? 'Connected through Telegram' : 'Preview mode'}
          </footer>
        </div>

        {!isBotRoute && <BottomNav activeTab={activeTab} onTabChange={handleTabChange} />}

        {tourOpen && (
          <TourOverlay
            tour={tour}
            canEarnXp={isVerified && profileData?.engagementLevel !== 'onboarded'}
            rawInitData={getRawInitData()}
            onClose={closeTour}
            onFinish={() => void refreshProfile()}
          />
        )}
      </div>
    </AppDataProvider>
  );
};

export default App;
