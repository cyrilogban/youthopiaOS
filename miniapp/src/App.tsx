import React from 'react';
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { useTelegram } from './hooks/useTelegram';
import { useHideNavOnScroll } from './hooks/useHideNavOnScroll';
import { AppDataProvider } from './context/AppData';
import { VerificationGate } from './components/VerificationGate';
import { TheoRoute } from './routes/theo/TheoRoute';

const App: React.FC = () => {
  const telegram = useTelegram();
  const { user, isInsideTelegram, verification, retryVerification } = telegram;
  const location = useLocation();
  const navigate = useNavigate();
  const navHidden = useHideNavOnScroll();

  const displayName = user?.firstName || 'Member';
  const initial = displayName[0]?.toUpperCase() || 'T';

  return (
    <AppDataProvider value={telegram}>
      <VerificationGate verification={verification} onRetry={retryVerification}>
      <div className={`app-shell${navHidden ? ' nav-hidden' : ''}`}>
        <div className="app-frame">
          <header className="app-header">
            <div>
              <div className="brand-kicker">Theo</div>
              <div className="brand-name">Scripture for your day</div>
            </div>

            <button className="profile-trigger" onClick={() => navigate('/theo/profile')} aria-label="Open your Scripture profile">
              <span className="profile-avatar">
                {user?.photoUrl ? <img src={user.photoUrl} alt={displayName} /> : initial}
              </span>
              <span className="profile-trigger-copy"><strong>{displayName}</strong><span>Scripture profile</span></span>
            </button>
          </header>

          <main key={location.pathname} className="tab-enter">
            <Routes>
              <Route path="/" element={<Navigate to="/theo/home" replace />} />
              <Route path="/home" element={<Navigate to="/theo/home" replace />} />
              <Route path="/theo/*" element={<TheoRoute />} />
              <Route path="/lusie/*" element={<Navigate to="/theo/home" replace />} />
              <Route path="/edie/*" element={<Navigate to="/theo/home" replace />} />
              <Route path="/susie/*" element={<Navigate to="/theo/home" replace />} />
              <Route path="/pete/*" element={<Navigate to="/theo/home" replace />} />
              <Route path="*" element={<Navigate to="/theo/home" replace />} />
            </Routes>
          </main>

          <footer style={{ marginTop: 28, color: 'var(--text-muted)', fontSize: 11, textAlign: 'center' }}>
            {isInsideTelegram ? 'Connected through Telegram' : 'Preview mode'}
          </footer>
        </div>

      </div>
      </VerificationGate>
    </AppDataProvider>
  );
};

export default App;
