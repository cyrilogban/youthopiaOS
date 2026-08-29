/**
 * UserProfile — our app's own shape for the person's stored YouThopiaOS record.
 */
export interface UserProfile {
  /** The YouThopiaOS display name. Optional — may be unset (null in the DB). */
  displayName?: string;
  /** Community engagement tier (e.g. 'new', 'active'). Always present. */
  engagementLevel: string;
  /** Lifetime XP earned across the community. */
  totalXp: number;
  /** Level derived from XP. */
  level: number;
  /** Community trust rating (Pete Bot security score). */
  trustScore?: number;
  /** Total quizzes played in Lusy Bot. */
  quizzesPlayed?: number;
  /** Quiz accuracy percentage (0-100%). */
  accuracyPct?: number;
}
