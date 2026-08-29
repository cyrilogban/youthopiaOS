/**
 * api.ts — the only file that knows the gateway's URL and HTTP contract.
 *
 * Mirror of telegram.ts: telegram.ts isolates the Telegram SDK, this isolates
 * our backend. fetchVerifiedUser asks the gateway "who am I?" and the gateway
 * answers only after HMAC-verifying the initData — the trust flip that is the
 * whole point of Module 3.
 */
import type { TelegramUser } from '../types/telegram';
import type { UserProfile } from '../types/profile';

// Dev default (localhost:8000); prod origin dynamically derived from window.location.origin when deployed.
const GATEWAY_URL =
  import.meta.env.VITE_GATEWAY_URL ??
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
    ? window.location.origin
    : 'http://localhost:8000');

/** The gateway's /me JSON — Telegram's native snake_case; optionals arrive as null. */
interface GatewayUser {
  id: number;
  first_name: string;
  last_name?: string | null;
  username?: string | null;
  language_code?: string | null;
  is_premium?: boolean | null;
  photo_url?: string | null;
}

/** Every honest outcome of asking the gateway who we are. */
export type VerifyResult =
  | { status: 'verified'; user: TelegramUser }
  | { status: 'unverified' }
  | { status: 'no-telegram' }
  | { status: 'error'; message: string };

function mapGatewayUser(u: GatewayUser): TelegramUser {
  return {
    id: u.id,
    firstName: u.first_name,
    lastName: u.last_name ?? undefined,
    username: u.username ?? undefined,
    photoUrl: u.photo_url ?? undefined,
    isPremium: u.is_premium ?? undefined,
  };
}

/** Ask the gateway to verify our Telegram initData and return the trusted user. */
export async function fetchVerifiedUser(rawInitData: string | null): Promise<VerifyResult> {
  if (!rawInitData) return { status: 'no-telegram' };

  let res: Response;
  try {
    res = await fetch(`${GATEWAY_URL}/me`, {
      headers: { Authorization: `tma ${rawInitData}` },
    });
  } catch {
    return { status: 'error', message: 'Could not reach the server.' };
  }

  if (res.status === 401) return { status: 'unverified' };
  if (!res.ok) return { status: 'error', message: `Unexpected response (${res.status}).` };

  try {
    const data = (await res.json()) as GatewayUser;
    return { status: 'verified', user: mapGatewayUser(data) };
  } catch {
    return { status: 'error', message: 'Malformed response from server.' };
  }
}

/** The gateway's /profile JSON — snake_case; display_name may be null. */
interface GatewayProfile {
  display_name?: string | null;
  engagement_level: string;
  total_xp: number;
  level: number;
}

/** Every honest outcome of asking the gateway for our YouThopiaOS profile. */
export type ProfileResult =
  | { status: 'ok'; profile: UserProfile }
  | { status: 'none' } // 404 — verified, but no YouThopiaOS account yet
  | { status: 'unverified' } // 401 — initData rejected (defensive; normally gated on verified)
  | { status: 'error'; message: string };

function mapGatewayProfile(p: GatewayProfile): UserProfile {
  return {
    displayName: p.display_name ?? undefined,
    engagementLevel: p.engagement_level,
    totalXp: p.total_xp,
    level: p.level,
  };
}

/** Ask the gateway for the verified user's stored profile + XP. */
export async function fetchProfile(rawInitData: string | null): Promise<ProfileResult> {
  if (!rawInitData) return { status: 'unverified' }; // no initData to authorize with

  let res: Response;
  try {
    res = await fetch(`${GATEWAY_URL}/profile`, {
      headers: { Authorization: `tma ${rawInitData}` },
    });
  } catch {
    return { status: 'error', message: 'Could not reach the server.' };
  }

  if (res.status === 401) return { status: 'unverified' };
  if (res.status === 404) return { status: 'none' };
  if (!res.ok) return { status: 'error', message: `Unexpected response (${res.status}).` };

  try {
    const data = (await res.json()) as GatewayProfile;
    return { status: 'ok', profile: mapGatewayProfile(data) };
  } catch {
    return { status: 'error', message: 'Malformed response from server.' };
  }
}
