/**
 * TabId — the 5 core sections of the YouThopiaOS Mini App dashboard.
 */
export type TabId = 'home' | 'bible' | 'quiz' | 'events' | 'community';

export interface TabConfig {
  id: TabId;
  label: string;
}
