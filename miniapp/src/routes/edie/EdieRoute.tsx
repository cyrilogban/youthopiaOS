import React from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { BotTabBar, type BotTab } from '../../components/BotTabBar';
import { EdieHome } from './EdieHome';
import { EdieCalendar } from './EdieCalendar';
import { EdieMyEvents } from './EdieMyEvents';
import { EdieBirthdays } from './EdieBirthdays';

const TABS: BotTab[] = [
  {
    id: 'home',
    label: 'Home',
    to: '/edie/home',
    icon: (
      <>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V21h14V9.5" />
        <path d="M9.5 21v-6h5v6" />
      </>
    ),
  },
  {
    id: 'calendar',
    label: 'Calendar',
    to: '/edie/calendar',
    icon: (
      <>
        <rect x="3" y="4.5" width="18" height="16" rx="3" />
        <path d="M3 9.5h18" />
        <path d="M8 3v3" />
        <path d="M16 3v3" />
      </>
    ),
  },
  {
    id: 'my-events',
    label: 'My Events',
    to: '/edie/my-events',
    icon: (
      <>
        <path d="M4 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2a2 2 0 0 0 0-4z" />
        <path d="M12 5v14" />
      </>
    ),
  },
  {
    id: 'birthdays',
    label: 'Birthdays',
    to: '/edie/birthdays',
    icon: (
      <>
        <path d="M5 21V11h14v10" />
        <path d="M3 21h18" />
        <path d="M12 11V7" />
        <path d="M12 7a2 2 0 1 0-2-2c0 1 2 2 2 2z" />
        <path d="M8 11V8" />
        <path d="M16 11V8" />
      </>
    ),
  },
];

/**
 * /edie - Edie's events and scheduling experience.
 * Nested tabs: home, calendar, my-events, birthdays.
 */
export const EdieRoute: React.FC = () => {
  const location = useLocation();
  const activeId = location.pathname.split('/')[2] || 'home';

  return (
    <div className="theme-edie">
      <div className="bot-identity">
        <span className="bot-mark">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4.5" width="18" height="16" rx="3" />
            <path d="M3 9.5h18" />
            <path d="M8 3v3" />
            <path d="M16 3v3" />
          </svg>
        </span>
        <div className="bot-identity-copy">
          <strong>Edie</strong>
          <span>@ediecalendarbot</span>
        </div>
        <span className="bot-identity-tag">Events Bot</span>
      </div>

      <Routes>
        <Route index element={<Navigate to="home" replace />} />
        <Route path="home" element={<EdieHome />} />
        <Route path="calendar" element={<EdieCalendar />} />
        <Route path="my-events" element={<EdieMyEvents />} />
        <Route path="birthdays" element={<EdieBirthdays />} />
        <Route path="*" element={<Navigate to="home" replace />} />
      </Routes>

      <BotTabBar tabs={TABS} activeId={activeId} />
    </div>
  );
};
