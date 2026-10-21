import React from 'react';
import { useNavigate } from 'react-router-dom';

export interface BotTab {
  id: string;
  label: string;
  to: string;
  icon: React.ReactNode;
}

interface BotTabBarProps {
  tabs: BotTab[];
  activeId: string;
}

/**
 * Layer 1 navigation: a bot's own tabs. Sits alone at the bottom of its route.
 * Bot switching lives in the identity header's switch sheet, never in this bar.
 */
export const BotTabBar: React.FC<BotTabBarProps> = ({ tabs, activeId }) => {
  const navigate = useNavigate();

  return (
    <nav
      aria-label="Bot navigation"
      className="bot-tabbar"
      style={{ gridTemplateColumns: `repeat(${tabs.length}, 1fr)` }}
    >
      {tabs.map((tab) => {
        const active = activeId === tab.id;
        return (
          <button
            key={tab.id}
            aria-current={active ? 'page' : undefined}
            onClick={() => navigate(tab.to)}
            className={`bot-tab${active ? ' is-active' : ''}`}
          >
            <svg
              width="21"
              height="21"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.15"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {tab.icon}
            </svg>
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
};
