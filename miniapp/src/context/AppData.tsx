import React, { createContext, useContext } from 'react';
import type { TelegramUser } from '../types/telegram';
import type { ProfileState, VerificationState } from '../hooks/useTelegram';

export interface AppData {
  user: TelegramUser | null;
  isInsideTelegram: boolean;
  verification: VerificationState;
  profile: ProfileState;
  refreshProfile: () => Promise<void>;
}

const AppDataContext = createContext<AppData | null>(null);

export const AppDataProvider: React.FC<{ value: AppData; children: React.ReactNode }> = ({ value, children }) => (
  <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>
);

export function useAppData(): AppData {
  const ctx = useContext(AppDataContext);
  if (!ctx) throw new Error('useAppData must be used inside AppDataProvider');
  return ctx;
}
