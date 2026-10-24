import React from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { YouVersionProvider } from '@youversion/platform-react-ui';
import { BotTabBar, type BotTab } from '../../components/BotTabBar';
import { BotIdentityBar } from '../../components/BotSwitcherSheet';
import { BibleTab } from '../../components/tabs/BibleTab';
import { TheoHome } from './TheoHome';
import { TheoSaved } from './TheoSaved';
import { TheoProfile } from './TheoProfile';

const YOUVERSION_APP_KEY = import.meta.env.VITE_YOUVERSION_APP_KEY || '';

const TABS: BotTab[] = [
  {
    id: 'home',
    label: 'Home',
    to: '/theo/home',
    icon: (
      <>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V21h14V9.5" />
        <path d="M9.5 21v-6h5v6" />
      </>
    ),
  },
  {
    id: 'bible',
    label: 'Bible',
    to: '/theo/bible',
    icon: (
      <>
        <path d="M5 19.5A2.5 2.5 0 0 1 7.5 17H20" />
        <path d="M7.5 3H20v19H7.5A2.5 2.5 0 0 1 5 19.5v-14A2.5 2.5 0 0 1 7.5 3z" />
        <path d="M10 7h6" />
      </>
    ),
  },
  {
    id: 'saved',
    label: 'Saved',
    to: '/theo/saved',
    icon: <path d="M19 21l-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />,
  },
  {
    id: 'profile',
    label: 'Profile',
    to: '/theo/profile',
    icon: (
      <>
        <circle cx="12" cy="8" r="4" />
        <path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1" />
      </>
    ),
  },
];

/**
 * /theo — Theodore's routed Mini App experience.
 * Nested tabs: home, bible, saved, profile.
 */
export const TheoRoute: React.FC = () => {
  const location = useLocation();
  const activeId = location.pathname.split('/')[2] || 'home';

  return (
    <YouVersionProvider
      appKey={YOUVERSION_APP_KEY}
      theme="light"
      includeAuth={false}
      appName="YouThopia Bible Community"
    >
      <div className="theme-theo">
        <BotIdentityBar
          botId="theo"
          tag="Daily Word"
          mark={
            <>
              <path d="M5 19.5A2.5 2.5 0 0 1 7.5 17H20" />
              <path d="M7.5 3H20v19H7.5A2.5 2.5 0 0 1 5 19.5v-14A2.5 2.5 0 0 1 7.5 3z" />
            </>
          }
        />

        <Routes>
          <Route index element={<Navigate to="home" replace />} />
          <Route path="home" element={<TheoHome />} />
          <Route path="bible" element={<BibleTab />} />
          <Route path="saved" element={<TheoSaved />} />
          <Route path="profile" element={<TheoProfile />} />
          <Route path="*" element={<Navigate to="home" replace />} />
        </Routes>

        <BotTabBar tabs={TABS} activeId={activeId} />
      </div>
    </YouVersionProvider>
  );
};

