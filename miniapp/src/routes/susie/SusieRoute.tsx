import React from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { BotTabBar, type BotTab } from '../../components/BotTabBar';
import { SusieHome } from './SusieHome';
import { SusieOnboarding } from './SusieOnboarding';
import { SusieDirectory } from './SusieDirectory';
import { SusieFaq } from './SusieFaq';

const TABS: BotTab[] = [
  {
    id: 'home',
    label: 'Home',
    to: '/susie/home',
    icon: (
      <>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V21h14V9.5" />
        <path d="M9.5 21v-6h5v6" />
      </>
    ),
  },
  {
    id: 'onboarding',
    label: 'Onboarding',
    to: '/susie/onboarding',
    icon: (
      <>
        <path d="M9 11l3 3 8-8" />
        <path d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9" />
      </>
    ),
  },
  {
    id: 'directory',
    label: 'Directory',
    to: '/susie/directory',
    icon: (
      <>
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </>
    ),
  },
  {
    id: 'faq',
    label: 'FAQ',
    to: '/susie/faq',
    icon: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M9.5 9a2.5 2.5 0 0 1 4.5 1.5c0 1.5-2 2-2 3.5" />
        <path d="M12 17.5h.01" />
      </>
    ),
  },
];

interface SusieRouteProps {
  onOpenTour?: () => void;
}

/**
 * /susie - Susie's hospitality and onboarding experience.
 * Nested tabs: home, onboarding, directory, faq.
 */
export const SusieRoute: React.FC<SusieRouteProps> = ({ onOpenTour }) => {
  const location = useLocation();
  const activeId = location.pathname.split('/')[2] || 'home';

  return (
    <div className="theme-susie">
      <div className="bot-identity">
        <span className="bot-mark">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7a8.5 8.5 0 0 1-.9-3.8 8.38 8.38 0 0 1 8.5-8.5 8.38 8.38 0 0 1 8.5 8.5z" />
          </svg>
        </span>
        <div className="bot-identity-copy">
          <strong>Susie</strong>
          <span>@susiehelpsbot</span>
        </div>
        <span className="bot-identity-tag">Welcome Bot</span>
      </div>

      <Routes>
        <Route index element={<Navigate to="home" replace />} />
        <Route path="home" element={<SusieHome onOpenTour={onOpenTour} />} />
        <Route path="onboarding" element={<SusieOnboarding onOpenTour={onOpenTour} />} />
        <Route path="directory" element={<SusieDirectory />} />
        <Route path="faq" element={<SusieFaq />} />
        <Route path="*" element={<Navigate to="home" replace />} />
      </Routes>

      <BotTabBar tabs={TABS} activeId={activeId} />
    </div>
  );
};
