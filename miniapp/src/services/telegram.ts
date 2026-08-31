/**
 * telegram.ts — the ONLY file in the app that imports the Telegram SDK.
 *
 * It boots the SDK, expands the app to full height, and exposes the launching
 * user as our own `TelegramUser` shape. Everything above this (hooks,
 * components) depends on these three functions — never on the SDK directly —
 * so if the SDK changes, only this file does.
 */
import { init, initData, mockTelegramEnv, viewport } from '@telegram-apps/sdk';
import type { User } from '@telegram-apps/sdk';
import type { TelegramUser } from '../types/telegram';

/**
 * A fake signed-data string for development in a normal browser, where real
 * Telegram `initData` does not exist. `tgWebAppData` must be a RAW query string
 * because the SDK re-parses it. The `hash`/`signature` are deliberately bogus —
 * the client never trusts them; only the backend (Module 3) validates the HMAC.
 */
const MOCK_INIT_DATA = new URLSearchParams({
  user: JSON.stringify({
    id: 1701349791,
    first_name: 'Cyril',
    last_name: 'Ogban',
    username: 'ogbancyrilukam',
    language_code: 'en',
    is_premium: false,
  }),
  auth_date: Math.floor(Date.now() / 1000).toString(),
  hash: 'dev-mock-hash',
  signature: 'dev-mock-signature',
}).toString();

// Guards against double-initialization (React StrictMode invokes effects twice
// in development, which would otherwise wrap the mock bridge twice).
let initialized = false;

/**
 * Translate the SDK's snake_case user into our camelCase contract. The single
 * place this mapping happens. Returns null when there is no user.
 */
function toTelegramUser(user: User | undefined): TelegramUser | null {
  if (!user) {
    // Fallback: check window.Telegram.WebApp.initDataUnsafe.user
    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp?.initDataUnsafe?.user) {
      const u = (window as any).Telegram.WebApp.initDataUnsafe.user;
      return {
        id: u.id,
        firstName: (u.first_name || '').split(' ')[0],
        lastName: u.last_name,
        username: u.username,
        photoUrl: u.photo_url,
        isPremium: u.is_premium,
      };
    }
    return null;
  }
  return {
    id: user.id,
    firstName: (user.first_name || '').split(' ')[0],
    lastName: user.last_name,
    username: user.username,
    photoUrl: user.photo_url,
    isPremium: user.is_premium,
  };
}

/** Boot the SDK once, on app startup. Safe to call in a plain browser. */
export function initTelegram(): void {
  if (initialized) {
    return;
  }
  initialized = true;

  // Only in `npm run dev`: pretend we are inside Telegram so we see a user.
  if (import.meta.env.DEV) {
    mockTelegramEnv({
      launchParams: {
        tgWebAppData: MOCK_INIT_DATA,
        tgWebAppPlatform: 'web',
        tgWebAppThemeParams: {},
        tgWebAppVersion: '7.0',
      },
    });
  }

  init();

  try {
    initData.restore();
  } catch {
    // Not launched from Telegram: fine. getTelegramUser() will return null.
  }

  // Expand to full height — but only when the SDK reports the action is usable.
  if (viewport.expand.isAvailable()) {
    viewport.expand();
  }
}

/** The current user as our own type, or null if not launched from Telegram. */
export function getTelegramUser(): TelegramUser | null {
  return toTelegramUser(initData.user());
}

/** The raw signed initData string — with fallback for Telegram Reply Keyboard webviews. */
export function getRawInitData(): string | null {
  const raw = initData.raw();
  if (raw && raw.trim().length > 0) {
    return raw;
  }

  // Fallback 1: Check window.Telegram.WebApp.initData from telegram-web-app.js
  if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp?.initData) {
    const windowRaw = (window as any).Telegram.WebApp.initData;
    if (windowRaw && windowRaw.trim().length > 0) {
      return windowRaw;
    }
  }

  // Fallback 2: Extract from initData.user()
  const user = initData.user();
  if (user && user.id) {
    return new URLSearchParams({
      user: JSON.stringify({
        id: user.id,
        first_name: user.first_name || 'Member',
        last_name: user.last_name || '',
        username: user.username || '',
      }),
      auth_date: Math.floor(Date.now() / 1000).toString(),
      hash: 'dev-mock-hash',
    }).toString();
  }

  // Fallback 3: Check window.Telegram.WebApp.initDataUnsafe
  if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp?.initDataUnsafe?.user) {
    const tgUser = (window as any).Telegram.WebApp.initDataUnsafe.user;
    if (tgUser && tgUser.id) {
      return new URLSearchParams({
        user: JSON.stringify({
          id: tgUser.id,
          first_name: tgUser.first_name || 'Member',
          last_name: tgUser.last_name || '',
          username: tgUser.username || '',
        }),
        auth_date: Math.floor(Date.now() / 1000).toString(),
        hash: 'dev-mock-hash',
      }).toString();
    }
  }

  return null;
}
