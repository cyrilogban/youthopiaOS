import { useEffect, useState } from 'react';
import { getRawInitData, getTelegramUser, initTelegram } from '../services/telegram';
import type { TelegramUser } from '../types/telegram';

interface UseTelegramResult {
  /** The launching user, or null when unavailable (e.g. a plain browser). */
  user: TelegramUser | null;
  /** True when Telegram launch data is present (real client or the dev mock). */
  isInsideTelegram: boolean;
}

/**
 * Boots the Telegram SDK once on mount and exposes the current user as reactive
 * React state. Components consume this hook instead of touching the service
 * directly, so the SDK wiring lives in exactly one place.
 */
export function useTelegram(): UseTelegramResult {
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isInsideTelegram, setIsInsideTelegram] = useState(false);

  // Empty dependency array -> run once, after the first render (on mount).
  useEffect(() => {
    initTelegram();
    setUser(getTelegramUser());
    setIsInsideTelegram(getRawInitData() !== null);
  }, []);

  return { user, isInsideTelegram };
}
