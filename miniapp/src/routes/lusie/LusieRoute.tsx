import React from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { BotTabBar, type BotTab } from '../../components/BotTabBar';
import { BotIdentityBar } from '../../components/BotSwitcherSheet';
import { LusieHome } from './LusieHome';
import { LusiePlay } from './LusiePlay';
import { LusieLeaderboard } from './LusieLeaderboard';
import { LusieProfile } from './LusieProfile';

const TABS: BotTab[] = [
  {
    id: 'home',
    label: 'Home',
    to: '/lusie/home',
    icon: (
      <>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V21h14V9.5" />
        <path d="M9.5 21v-6h5v6" />
      </>
    ),
  },
  {
    id: 'play',
    label: 'Play',
    to: '/lusie/play',
    icon: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M10 8.5l6 3.5-6 3.5z" />
      </>
    ),
  },
  {
    id: 'leaderboard',
    label: 'Leaderboard',
    to: '/lusie/leaderboard',
    icon: (
      <>
        <path d="M8 21h8" />
        <path d="M12 17v4" />
        <path d="M7 4h10v5a5 5 0 0 1-10 0z" />
        <path d="M7 6H5a2 2 0 0 0 2 2" />
        <path d="M17 6h2a2 2 0 0 1-2 2" />
      </>
    ),
  },
  {
    id: 'profile',
    label: 'Profile',
    to: '/lusie/profile',
    icon: (
      <>
        <circle cx="12" cy="8" r="4" />
        <path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1" />
      </>
    ),
  },
];

/**
 * /lusie - Lusie's games, quizzes and leaderboard experience.
 * Nested tabs: home, play, leaderboard, profile.
 */
export const LusieRoute: React.FC = () => {
  const location = useLocation();
  const activeId = location.pathname.split('/')[2] || 'home';

  return (
    <div className="theme-lusie">
      <BotIdentityBar
        botId="lusie"
        tag="Games & XP"
        mark={
          <>
            <circle cx="12" cy="12" r="9" />
            <circle cx="12" cy="12" r="4" />
            <circle cx="12" cy="12" r="1" />
          </>
        }
      />

      <Routes>
        <Route index element={<Navigate to="home" replace />} />
        <Route path="home" element={<LusieHome />} />
        <Route path="play" element={<LusiePlay />} />
        <Route path="leaderboard" element={<LusieLeaderboard />} />
        <Route path="profile" element={<LusieProfile />} />
        <Route path="*" element={<Navigate to="home" replace />} />
      </Routes>

      <BotTabBar tabs={TABS} activeId={activeId} />
    </div>
  );
};
