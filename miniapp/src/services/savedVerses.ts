/**
 * Local saved verses store (no backend yet). The Saved tab reads this, and the
 * Save action on feed posts writes to it. Swaps to a gateway endpoint later.
 */
export interface SavedVerse {
  id: string;
  reference: string;
  text: string;
  translation: string;
  savedAt: number;
}

const KEY = 'youthopia_saved_verses_v1';

export function getSavedVerses(): SavedVerse[] {
  try {
    const raw = window.localStorage.getItem(KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function isVerseSaved(id: string): boolean {
  return getSavedVerses().some((verse) => verse.id === id);
}

export function toggleSavedVerse(verse: SavedVerse): { saved: boolean; list: SavedVerse[] } {
  const list = getSavedVerses();
  const index = list.findIndex((item) => item.id === verse.id);
  let saved: boolean;
  if (index >= 0) {
    list.splice(index, 1);
    saved = false;
  } else {
    list.unshift(verse);
    saved = true;
  }
  try {
    window.localStorage.setItem(KEY, JSON.stringify(list.slice(0, 200)));
  } catch {
    // storage full or blocked; keep the in-memory result only
  }
  return { saved, list };
}
