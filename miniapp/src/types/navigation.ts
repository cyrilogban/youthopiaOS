/**
 * TabId - the 5 core sections of the YouThopiaOS Mini App dashboard.
 */
export type TabId = 'home' | 'bible' | 'quiz' | 'events' | 'community';

export interface TabConfig {
  id: TabId;
  label: string;
}

/**
 * BotRouteId - the routed entry points each bot opens directly.
 * One React app, one deployment, five bot routes plus the shared home dashboard.
 */
export type BotRouteId = 'home' | 'theo' | 'lusie' | 'pete' | 'edie' | 'susie';

/**
 * Path each dashboard tab lives on. This is the tab -> route mapping from the
 * architecture decision (Home -> /home, Bible -> /theo, Quiz -> /lusie,
 * Events -> /edie, Community -> /susie).
 */
export const TAB_ROUTES: Record<TabId, string> = {
  home: '/home',
  bible: '/theo',
  quiz: '/lusie',
  events: '/edie',
  community: '/susie',
};

const PATH_TO_TAB: Record<string, TabId> = {
  '/home': 'home',
  '/theo': 'bible',
  '/lusie': 'quiz',
  '/edie': 'events',
  '/susie': 'community',
  '/pete': 'community',
};

/** Route path for a dashboard tab. */
export function pathForTab(tab: TabId): string {
  return TAB_ROUTES[tab];
}

/** Which dashboard tab a route path belongs to (defaults to home). */
export function tabForPath(pathname: string): TabId {
  const normalized = pathname.replace(/\/+$/, '') || '/home';
  return PATH_TO_TAB[normalized] ?? 'home';
}
