import { useEffect, useState } from 'react';
import { getRawInitData, getTelegramUser, initTelegram } from '../services/telegram';
import { fetchProfile, fetchVerifiedUser, type ProfileResult, type VerifyResult } from '../services/api';
import type { TelegramUser } from '../types/telegram';

/** 'loading' precedes any server answer; after that it's whatever the gateway said. */
export type VerificationState = { status: 'loading' } | VerifyResult;

/** 'idle' until verification succeeds; then 'loading' → whatever /profile said. */
export type ProfileState = { status: 'idle' } | { status: 'loading' } | ProfileResult;

interface UseTelegramResult {
  /** The launching user as the client *claims* (unverified), or null in a plain browser. */
  user: TelegramUser | null;
  /** True when Telegram launch data is present (real client or the dev mock). */
  isInsideTelegram: boolean;
  /** What the gateway said when asked to verify the initData signature. */
  verification: VerificationState;
  /** The YouThopiaOS profile behind a verified user; 'idle' until verification succeeds. */
  profile: ProfileState;
}

/**
 * Boots the Telegram SDK once on mount, exposes the client-claimed user, and
 * asks the gateway to verify that claim. Components consume this hook instead of
 * touching the services directly, so the SDK + gateway wiring lives in one place.
 */
export function useTelegram(): UseTelegramResult {
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isInsideTelegram, setIsInsideTelegram] = useState(false);
  const [verification, setVerification] = useState<VerificationState>({ status: 'loading' });
  const [profile, setProfile] = useState<ProfileState>({ status: 'idle' });

  // Empty dependency array -> run once, after the first render (on mount).
  useEffect(() => {
    initTelegram();
    setUser(getTelegramUser());
    const raw = getRawInitData();
    setIsInsideTelegram(raw !== null);

    // The effect callback must stay synchronous (it may only return a cleanup
    // fn, never a Promise), so run the async verify in an inner IIFE and ignore
    // a late resolve if we've unmounted (also neutralizes StrictMode's dev
    // double-invoke).
    let cancelled = false;
    void (async () => {
      const result = await fetchVerifiedUser(raw);
      if (cancelled) return;
      setVerification(result);

      // Only reach into our own stored data once the server has proven who they
      // are. Unverified / no-telegram / error users never trigger a /profile call.
      if (result.status === 'verified') {
        setProfile({ status: 'loading' });
        const loaded = await fetchProfile(raw);
        if (!cancelled) setProfile(loaded);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return { user, isInsideTelegram, verification, profile };
}
