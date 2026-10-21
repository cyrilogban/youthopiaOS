import React from 'react';

export type SwitcherBotId = 'theo' | 'lusie' | 'pete' | 'edie' | 'susie';

export interface SwitcherBot {
  id: SwitcherBotId;
  name: string;
  route: string;
  accent: string;
  accentSoft: string;
  icon: React.ReactNode;
  /** @handle shown in the identity header and in the switch sheet. */
  handle: string;
  /** One-line role badge, reused by the identity header and the switch sheet. */
  role: string;
}

/**
 * The five doors into the one Mini App, in switch-sheet order.
 * Kept as data so a community can render only its enabled bots later (Decision 3).
 */
export const BOTS: SwitcherBot[] = [
  {
    id: 'theo',
    name: 'Theo',
    route: '/theo',
    accent: '#5b4be5',
    accentSoft: '#eef0fe',
    handle: '@theobiblebot',
    role: 'Daily Word',
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
    handle: '@lusiequizbot',
    role: 'Games & XP',
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
    handle: '@petemodbot',
    role: 'Safety Bot',
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
    handle: '@ediecalendarbot',
    role: 'Events Bot',
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
    handle: '@susiehelpsbot',
    role: 'Welcome Bot',
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
