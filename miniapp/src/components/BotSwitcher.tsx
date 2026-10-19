import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export type SwitcherBotId = 'theo' | 'lusie' | 'pete' | 'edie' | 'susie';

export interface SwitcherBot {
  id: SwitcherBotId;
  name: string;
  route: string;
  accent: string;
  accentSoft: string;
  icon: React.ReactNode;
}

/**
 * The five doors into the one Mini App, in the order shown by the switcher.
 * Kept as data so a community can render only its enabled bots later (Decision 3).
 */
export const BOTS: SwitcherBot[] = [
  {
    id: 'theo',
    name: 'Theo',
    route: '/theo',
    accent: '#5b4be5',
    accentSoft: '#eef0fe',
    icon: (
      <>
        <path d="M5 19.5A2.5 2.5 0 0 1 7.5 17H20" />
        <path d="M7.5 3H20v19H7.5A2.5 2.5 0 0 1 5 19.5v-14A2.5 2.5 0 0 1 7.5 3z" />
        <path d="M10 7h6" />
      </>
    ),
  },
  {
    id: 'lusie',
    name: 'Lusie',
    route: '/lusie',
    accent: '#d98a1f',
    accentSoft: '#fbf1e0',
    icon: (
      <>
        <path d="M7 4h10v5a5 5 0 0 1-10 0z" />
        <path d="M7 6H4.5A2.5 2.5 0 0 0 7 10.5" />
        <path d="M17 6h2.5A2.5 2.5 0 0 1 17 10.5" />
        <path d="M12 14v3" />
        <path d="M8.5 21h7l-1-3.5h-5z" />
      </>
    ),
  },
  {
    id: 'pete',
    name: 'Pete',
    route: '/pete',
    accent: '#3b6fb6',
    accentSoft: '#eaf1f9',
    icon: (
      <>
        <path d="M12 3l7 2.6v5.1c0 4.3-2.9 7.3-7 8.8-4.1-1.5-7-4.5-7-8.8V5.6z" />
        <path d="M9.3 11.8l1.9 1.9 3.5-3.6" />
      </>
    ),
  },
  {
    id: 'edie',
    name: 'Edie',
    route: '/edie',
    accent: '#0f9d8f',
    accentSoft: '#e7f6f4',
    icon: (
      <>
        <rect x="3" y="4.5" width="18" height="16" rx="3" />
        <path d="M8 2.5v4" />
        <path d="M16 2.5v4" />
        <path d="M3 10h18" />
      </>
    ),
  },
  {
    id: 'susie',
    name: 'Susie',
    route: '/susie',
    accent: '#e1568b',
    accentSoft: '#fceef4',
    icon: (
      <>
        <path d="M16 20v-1.5a3.5 3.5 0 0 0-3.5-3.5h-6A3.5 3.5 0 0 0 3 18.5V20" />
        <circle cx="9.5" cy="7.5" r="3.5" />
        <path d="M21 20v-1.2a3 3 0 0 0-2.2-2.9" />
        <path d="M16.8 4.2a3.5 3.5 0 0 1 0 6.6" />
      </>
    ),
  },
];

/**
 * Layer 2 navigation: the cross-bot switcher. Persistent across every route,
 * sitting beneath the bot's own tab bar. One tap moves between bots without
 * leaving the Mini App (Decision 3).
 */
export const BotSwitcher: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const activeId = location.pathname.match(/^\/(theo|lusie|pete|edie|susie)(?:\/|$)/)?.[1];

  // On a bot route the switcher docks beneath that bot's tab bar (one panel);
  // on /home it floats on its own.
  return (
    <nav aria-label="Switch bot" className={`bot-switcher${activeId ? ' is-attached' : ''}`}>
      {BOTS.map((bot) => {
        const active = bot.id === activeId;
        return (
          <button
            key={bot.id}
            aria-current={active ? 'page' : undefined}
            aria-label={bot.name}
            onClick={() => navigate(bot.route)}
            className={`bot-switch${active ? ' is-active' : ''}`}
            style={active ? { color: bot.accent, background: bot.accentSoft } : undefined}
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.1"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {bot.icon}
            </svg>
            <span className="bot-switch-name">{active ? bot.name : ''}</span>
          </button>
        );
      })}
    </nav>
  );
};
