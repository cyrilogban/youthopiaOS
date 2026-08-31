import React from 'react';
import type { TabId } from '../types/navigation';

interface BottomNavProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

// Crisp inline vector SVG icons (20x20)
const HomeIcon: React.FC<{ active: boolean }> = ({ active }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke={active ? 'var(--primary-purple, #6d28d9)' : '#94a3b8'}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect x="3" y="3" width="7" height="7" rx="1.5" />
    <rect x="14" y="3" width="7" height="7" rx="1.5" />
    <rect x="14" y="14" width="7" height="7" rx="1.5" />
    <rect x="3" y="14" width="7" height="7" rx="1.5" />
  </svg>
);

const BibleIcon: React.FC<{ active: boolean }> = ({ active }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke={active ? 'var(--primary-purple, #6d28d9)' : '#94a3b8'}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
  </svg>
);

const QuizIcon: React.FC<{ active: boolean }> = ({ active }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke={active ? 'var(--primary-purple, #6d28d9)' : '#94a3b8'}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10" />
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

const EventsIcon: React.FC<{ active: boolean }> = ({ active }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke={active ? 'var(--primary-purple, #6d28d9)' : '#94a3b8'}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
);

const CommunityIcon: React.FC<{ active: boolean }> = ({ active }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke={active ? 'var(--primary-purple, #6d28d9)' : '#94a3b8'}
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

export const BottomNav: React.FC<BottomNavProps> = ({ activeTab, onTabChange }) => {
  const tabs: { id: TabId; label: string; Icon: React.FC<{ active: boolean }> }[] = [
    { id: 'home', label: 'Home', Icon: HomeIcon },
    { id: 'bible', label: 'Bible', Icon: BibleIcon },
    { id: 'quiz', label: 'Quiz', Icon: QuizIcon },
    { id: 'events', label: 'Events', Icon: EventsIcon },
    { id: 'community', label: 'Community', Icon: CommunityIcon },
  ];

  return (
    <nav
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: 'rgba(255, 255, 255, 0.92)',
        backdropFilter: 'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
        borderTop: '1px solid var(--slate-200)',
        boxShadow: '0 -6px 24px rgba(15, 23, 42, 0.06)',
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        padding: '6px 0 12px 0',
        zIndex: 1000,
        maxWidth: '480px',
        margin: '0 auto',
      }}
    >
      {tabs.map(({ id, label, Icon }) => {
        const active = activeTab === id;
        return (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            style={{
              background: 'none',
              border: 'none',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 4,
              cursor: 'pointer',
              padding: '8px 12px',
              color: active ? 'var(--primary-purple)' : 'var(--text-muted)',
              fontWeight: active ? 700 : 400,
              fontSize: 11,
              transition: 'color 0.15s var(--ease)',
              position: 'relative',
            }}
          >
            {active && (
              <span
                style={{
                  position: 'absolute',
                  top: -8,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: 28,
                  height: 3,
                  borderRadius: 2,
                  background: 'var(--primary-purple)',
                }}
              />
            )}
            <span
              style={{
                backgroundColor: active ? 'var(--purple-50)' : 'transparent',
                borderRadius: 'var(--radius-md)',
                padding: '5px 12px',
                transition: 'background 0.15s var(--ease)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Icon active={active} />
            </span>
            <span>{label}</span>
          </button>
        );
      })}
    </nav>
  );
};
