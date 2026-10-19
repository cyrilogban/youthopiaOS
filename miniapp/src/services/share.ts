/**
 * Sharing helpers for feed posts. Prefers the native share sheet, falls back to
 * Telegram's share deep link, then to the clipboard.
 */

const SHARE_ORIGIN = 'https://youthopiaos.onrender.com/theo';

interface TelegramWebAppShare {
  openTelegramLink?: (url: string) => void;
}

function telegramWebApp(): TelegramWebAppShare | undefined {
  return (window as unknown as { Telegram?: { WebApp?: TelegramWebAppShare } }).Telegram?.WebApp;
}

export async function shareText(title: string, text: string): Promise<'shared' | 'copied' | 'failed'> {
  const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(SHARE_ORIGIN)}&text=${encodeURIComponent(text)}`;

  if (typeof navigator !== 'undefined' && 'share' in navigator) {
    try {
      await navigator.share({ title, text });
      return 'shared';
    } catch {
      // dismissed or unsupported; fall through
    }
  }

  try {
    const tg = telegramWebApp();
    if (tg?.openTelegramLink) {
      tg.openTelegramLink(shareUrl);
      return 'shared';
    }
    window.open(shareUrl, '_blank', 'noopener,noreferrer');
    return 'shared';
  } catch {
    // fall through to clipboard
  }

  return (await copyText(text)) ? 'copied' : 'failed';
}

export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}
