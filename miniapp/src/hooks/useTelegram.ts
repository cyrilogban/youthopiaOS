import { useCallback, useEffect, useRef, useState } from 'react';
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
  /** Re-runs the /profile call (after XP changes, e.g. finishing the tour). */
  refreshProfile: () => Promise<void>;
  /** Re-runs verification with the gateway (used by the root gate's retry). */
  retryVerification: () => Promise<void>;
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
  const rawInitDataRef = useRef<string | null>(null);

  // Verify the launch claim with the gateway, then — only once verified — load
  // the stored profile. Reused on mount and by the gate's retry, so a rejected
  // session can be re-checked without a full reload.
  const runVerification = useCallback(async () => {
    const raw = rawInitDataRef.current;
    setVerification({ status: 'loading' });
    setProfile({ status: 'idle' });

    const result = await fetchVerifiedUser(raw);
    setVerification(result);

    // Only reach into our own stored data once the server has proven who they
    // are. Unverified / no-telegram / error users never trigger a /profile call.
    if (raw && result.status === 'verified') {
      setProfile({ status: 'loading' });
      setProfile(await fetchProfile(raw));
    }
  }, []);

  // Boot once: init the SDK, read the launch context, then verify.
  useEffect(() => {
    initTelegram();
    setUser(getTelegramUser());
    const raw = getRawInitData();
    rawInitDataRef.current = raw;
    setIsInsideTelegram(raw !== null);
    void runVerification();
  }, [runVerification]);

  const refreshProfile = useCallback(async () => {
    const raw = rawInitDataRef.current;
    if (!raw) return;
    setProfile({ status: 'loading' });
    setProfile(await fetchProfile(raw));
  }, []);

  return {
    user,
    isInsideTelegram,
    verification,
    profile,
    refreshProfile,
    retryVerification: runVerification,
  };
}
