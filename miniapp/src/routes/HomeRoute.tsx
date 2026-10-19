import React from 'react';
import { HomeTab } from '../components/tabs/HomeTab';
import type { ProfileState } from '../hooks/useTelegram';
import type { TelegramUser } from '../types/telegram';
import type { TabId } from '../types/navigation';

interface HomeRouteProps {
  user: TelegramUser | null;
  profile: ProfileState;
  verified: boolean;
  onNavigate: (tab: TabId) => void;
}

/**
 * /home - the shared YouThopiaOS dashboard (the current Home tab).
 */
export const HomeRoute: React.FC<HomeRouteProps> = ({ user, profile, verified, onNavigate }) => (
  <HomeTab user={user} profile={profile} verified={verified} onNavigate={onNavigate} />
);
