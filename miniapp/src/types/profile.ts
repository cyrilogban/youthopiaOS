/**
 * UserProfile — our app's own shape for the person's stored YouThopiaOS record.
 *
 * Sibling to types/telegram.ts: that models *who Telegram says you are*; this
 * models *what YouThopiaOS knows about you* (profile + XP). The gateway's
 * snake_case /profile JSON is mapped onto this in exactly one place —
 * src/services/api.ts — so the rest of the app depends only on this contract.
 *
 * These are the only fields the gateway's UserProfile response-model exposes;
 * internal columns (trust_score, id, timestamps) never reach the client.
 */
export interface UserProfile {
  /** The YouThopiaOS display name. Optional — may be unset (null in the DB); fall back to the Telegram first name. */
  displayName?: string;
  /** Community engagement tier (e.g. 'new', 'active'). Always present. */
  engagementLevel: string;
  /** Lifetime XP earned across the community. */
  totalXp: number;
  /** Level derived from XP. */
  level: number;
}
