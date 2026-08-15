/**
 * TelegramUser — our app's own shape for the person who launched the Mini App.
 *
 * We deliberately do NOT re-export the SDK's `User` type. This interface is the
 * single contract the rest of the app depends on. The SDK's (snake_case) shape
 * is mapped onto this in exactly one place — src/services/telegram.ts. So if
 * Telegram renames a field, or we later source the user from our own backend,
 * only that mapping changes; every component keeps working.
 */
export interface TelegramUser {
  /** Unique, stable Telegram id for this person. Always present. */
  id: number;
  /** First name. Telegram guarantees this, so it is required. */
  firstName: string;
  /** Last name. Optional — many users never set one. */
  lastName?: string;
  /** @username. Optional — not every account has one. */
  username?: string;
  /** Profile photo URL. Only provided in some launch contexts. */
  photoUrl?: string;
  /** True if the user has Telegram Premium. */
  isPremium?: boolean;
}
