/**
 * api.ts — the only file that knows the gateway's URL and HTTP contract.
 */
import type { TelegramUser } from '../types/telegram';
import type { UserProfile } from '../types/profile';

// Dev default (localhost:8000); prod origin dynamically derived from window.location.origin when deployed.
const GATEWAY_URL =
  import.meta.env.VITE_GATEWAY_URL ??
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
    ? window.location.origin
    : 'http://localhost:8000');

interface GatewayUser {
  id: number;
  first_name: string;
  last_name?: string | null;
  username?: string | null;
  language_code?: string | null;
  is_premium?: boolean | null;
  photo_url?: string | null;
}

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

interface GatewayProfile {
  display_name?: string | null;
  engagement_level: string;
  total_xp: number;
  level: number;
  trust_score?: number | null;
  quizzes_played?: number | null;
  accuracy_pct?: number | null;
}

export type ProfileResult =
  | { status: 'ok'; profile: UserProfile }
  | { status: 'none' }
  | { status: 'unverified' }
  | { status: 'error'; message: string };

function mapGatewayProfile(p: GatewayProfile): UserProfile {
  return {
    displayName: p.display_name ?? undefined,
    engagementLevel: p.engagement_level,
    totalXp: p.total_xp,
    level: p.level,
    trustScore: p.trust_score ?? 100,
    quizzesPlayed: p.quizzes_played ?? 0,
    accuracyPct: p.accuracy_pct ?? 100,
  };
}

export async function fetchProfile(rawInitData: string | null): Promise<ProfileResult> {
  if (!rawInitData) return { status: 'unverified' };

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

export interface UserSettings {
  translation: string;
  dailyDevotional: boolean;
}

export async function fetchSettings(rawInitData: string | null): Promise<UserSettings> {
  if (!rawInitData) return { translation: 'KJV', dailyDevotional: true };
  try {
    const res = await fetch(`${GATEWAY_URL}/api/settings`, {
      headers: { Authorization: `tma ${rawInitData}` },
    });
    if (!res.ok) return { translation: 'KJV', dailyDevotional: true };
    const data = await res.json();
    return { translation: data.translation, dailyDevotional: data.daily_devotional };
  } catch {
    return { translation: 'KJV', dailyDevotional: true };
  }
}

export async function updateSettings(rawInitData: string | null, settings: UserSettings): Promise<boolean> {
  if (!rawInitData) return false;
  try {
    const res = await fetch(`${GATEWAY_URL}/api/settings`, {
      method: 'PUT',
      headers: {
        Authorization: `tma ${rawInitData}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        translation: settings.translation,
        daily_devotional: settings.dailyDevotional,
      }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export interface LeaderboardItem {
  displayName?: string;
  totalXp: number;
  level: number;
}

export async function fetchLeaderboard(): Promise<LeaderboardItem[]> {
  try {
    const res = await fetch(`${GATEWAY_URL}/api/leaderboard`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.map((item: any) => ({
      displayName: item.display_name ?? undefined,
      totalXp: item.total_xp,
      level: item.level,
    }));
  } catch {
    return [];
  }
}

export interface EventItem {
  id?: string;
  title: string;
  startsAt: string;
  category?: string;
  location?: string;
}

export async function fetchEvents(): Promise<EventItem[]> {
  try {
    const res = await fetch(`${GATEWAY_URL}/api/events`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.map((item: any) => ({
      id: item.id,
      title: item.title,
      startsAt: item.starts_at,
      category: item.category,
      location: item.location,
    }));
  } catch {
    return [];
  }
}

export interface VotdItem {
  reference: string;
  text: string;
  translation: string;
}

export async function fetchVotd(translation: string = 'KJV'): Promise<VotdItem> {
  try {
    const res = await fetch(`${GATEWAY_URL}/api/votd?translation=${encodeURIComponent(translation)}`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    return {
      reference: data.reference,
      text: data.text,
      translation: data.translation,
    };
  } catch {
    return {
      reference: 'Jeremiah 29:11',
      text: 'For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.',
      translation: translation.toUpperCase(),
    };
  }
}
