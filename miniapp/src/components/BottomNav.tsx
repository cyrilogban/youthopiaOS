import React from 'react';
import type { TabId } from '../types/navigation';

interface BottomNavProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

const Icon: React.FC<{ active: boolean; path: React.ReactNode }> = ({ active, path }) => (
  <svg
    width="21"
    height="21"
    viewBox="0 0 24 24"
    fill="none"
    stroke={active ? 'var(--primary-purple)' : 'var(--text-muted)'}
    strokeWidth="2.15"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    {path}
  </svg>
);

export const BottomNav: React.FC<BottomNavProps> = ({ activeTab, onTabChange }) => {
  const tabs: { id: TabId; label: string; path: React.ReactNode }[] = [
    {
      id: 'home',
      label: 'Home',
      path: (
        <>
          <rect x="3" y="3" width="7" height="7" rx="2" />
          <rect x="14" y="3" width="7" height="7" rx="2" />
          <rect x="14" y="14" width="7" height="7" rx="2" />
          <rect x="3" y="14" width="7" height="7" rx="2" />
        </>
      ),
    },
    {
      id: 'bible',
      label: 'Bible',
      path: (
        <>
          <path d="M5 19.5A2.5 2.5 0 0 1 7.5 17H20" />
          <path d="M7.5 3H20v19H7.5A2.5 2.5 0 0 1 5 19.5v-14A2.5 2.5 0 0 1 7.5 3z" />
          <path d="M10 7h6" />
        </>
      ),
    },
    {
      id: 'quiz',
      label: 'Lusy',
      path: (
        <>
          <circle cx="12" cy="12" r="9" />
          <path d="M9.5 9.3a2.7 2.7 0 0 1 5.1 1.2c0 1.8-2.6 2.3-2.6 4" />
          <path d="M12 18h.01" />
        </>
      ),
    },
    {
      id: 'events',
      label: 'Eddy',
      path: (
        <>
          <rect x="3" y="4.5" width="18" height="16" rx="3" />
          <path d="M8 2.5v4" />
          <path d="M16 2.5v4" />
          <path d="M3 10h18" />
        </>
      ),
    },
    {
      id: 'community',
      label: 'Hub',
      path: (
        <>
          <path d="M16 20v-1.5a3.5 3.5 0 0 0-3.5-3.5h-6A3.5 3.5 0 0 0 3 18.5V20" />
          <circle cx="9.5" cy="7.5" r="3.5" />
          <path d="M21 20v-1.2a3 3 0 0 0-2.2-2.9" />
          <path d="M16.8 4.2a3.5 3.5 0 0 1 0 6.6" />
        </>
      ),
    },
  ];

  return (
    <nav
      aria-label="Main navigation"
      style={{
        position: 'fixed',
        left: '50%',
        bottom: 12,
        transform: 'translateX(-50%)',
        width: 'calc(100% - 24px)',
        maxWidth: 500,
        minHeight: 70,
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        alignItems: 'center',
        gap: 4,
        padding: 6,
        borderRadius: 28,
        background: 'rgba(255,255,255,0.9)',
        border: '1px solid rgba(221, 214, 254, 0.78)',
        boxShadow: '0 18px 50px rgba(41, 19, 69, 0.18)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        zIndex: 1000,
      }}
    >
      {tabs.map(({ id, label, path }) => {
        const active = activeTab === id;
        return (
          <button
            key={id}
            aria-current={active ? 'page' : undefined}
            onClick={() => onTabChange(id)}
            style={{
              minWidth: 0,
              minHeight: 58,
              border: 0,
              borderRadius: 22,
              background: active ? 'var(--purple-50)' : 'transparent',
              color: active ? 'var(--primary-purple)' : 'var(--text-muted)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 5,
              fontSize: 10,
              fontWeight: active ? 900 : 750,
              cursor: 'pointer',
              transition: 'background 0.18s var(--ease), color 0.18s var(--ease)',
            }}
          >
            <Icon active={active} path={path} />
            <span>{label}</span>
          </button>
        );
      })}
    </nav>
  );
};
