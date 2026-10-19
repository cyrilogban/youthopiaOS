import React from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { BotTabBar, type BotTab } from '../../components/BotTabBar';
import { PeteHome } from './PeteHome';
import { PeteTrust } from './PeteTrust';
import { PeteHistory } from './PeteHistory';
import { PeteRules } from './PeteRules';

const TABS: BotTab[] = [
  {
    id: 'home',
    label: 'Home',
    to: '/pete/home',
    icon: (
      <>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V21h14V9.5" />
        <path d="M9.5 21v-6h5v6" />
      </>
    ),
  },
  {
    id: 'trust',
    label: 'Trust',
    to: '/pete/trust',
    icon: (
      <>
        <path d="M12 3l7 3v5c0 4.4-3 8.3-7 10-4-1.7-7-5.6-7-10V6z" />
        <path d="M9 12l2 2 4-4" />
      </>
    ),
  },
  {
    id: 'history',
    label: 'History',
    to: '/pete/history',
    icon: (
      <>
        <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
        <path d="M3 3v5h5" />
        <path d="M12 8v4l3 2" />
      </>
    ),
  },
  {
    id: 'rules',
    label: 'Rules',
    to: '/pete/rules',
    icon: (
      <>
        <path d="M6 3h9l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" />
        <path d="M14 3v5h5" />
        <path d="M9 13h6" />
        <path d="M9 17h6" />
      </>
    ),
  },
];

/**
 * /pete - Pete's safety and trust experience.
 * Nested tabs: home, trust, history, rules.
 */
export const PeteRoute: React.FC = () => {
  const location = useLocation();
  const activeId = location.pathname.split('/')[2] || 'home';

  return (
    <div className="theme-pete">
      <div className="bot-identity">
        <span className="bot-mark">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 3l7 3v5c0 4.4-3 8.3-7 10-4-1.7-7-5.6-7-10V6z" />
          </svg>
        </span>
        <div className="bot-identity-copy">
          <strong>Pete</strong>
          <span>@petemodbot</span>
        </div>
        <span className="bot-identity-tag">Safety Bot</span>
      </div>

      <Routes>
        <Route index element={<Navigate to="home" replace />} />
        <Route path="home" element={<PeteHome />} />
        <Route path="trust" element={<PeteTrust />} />
        <Route path="history" element={<PeteHistory />} />
        <Route path="rules" element={<PeteRules />} />
        <Route path="*" element={<Navigate to="home" replace />} />
      </Routes>

      <BotTabBar tabs={TABS} activeId={activeId} />
    </div>
  );
};
