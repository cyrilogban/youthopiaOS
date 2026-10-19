export interface TrustTier {
  label: string;
  min: number;
  tone: 'success' | 'purple' | 'warning';
  description: string;
}

export const TRUST_TIERS: TrustTier[] = [
  { label: 'Verified Member', min: 100, tone: 'success', description: 'Full standing. Clean record and oriented.' },
  { label: 'Active YouTopian', min: 80, tone: 'purple', description: 'In good standing, with a small action or two on record.' },
  { label: 'Under Observation', min: 0, tone: 'warning', description: 'Recent moderation actions. An accepted appeal restores standing.' },
];

export function trustTier(score: number): TrustTier {
  if (score >= 100) return TRUST_TIERS[0];
  if (score >= 80) return TRUST_TIERS[1];
  return TRUST_TIERS[2];
}

export interface TrustEvent {
  action: string;
  delta: number;
  note: string;
}

export const TRUST_EVENTS: TrustEvent[] = [
  { action: 'Warning issued', delta: -10, note: 'Each formal warning from the moderation team.' },
  { action: 'Automatic mute', delta: -20, note: 'Reaching three warnings.' },
  { action: 'Automatic ban', delta: -50, note: 'Reaching five warnings.' },
  { action: 'Accepted appeal', delta: 100, note: 'Restores your score to the maximum of 100.' },
  { action: 'Complete orientation', delta: 50, note: 'Finishing the YouThopia Tour.' },
];

export interface SafetyFeature {
  title: string;
  description: string;
}

export const SAFETY_FEATURES: SafetyFeature[] = [
  { title: 'Captcha verification', description: 'Automated new-member checks before anyone can post.' },
  { title: 'Spam and raid shield', description: 'Instant detection of links, floods, and harmful content.' },
  { title: 'Transparent record', description: 'Every warning is logged and visible to you.' },
  { title: 'Appeals', description: 'Appeal any action directly to the community admins.' },
];

export interface RuleEntry {
  title: string;
  description: string;
}

export const RULES: RuleEntry[] = [
  { title: 'Love God, love people', description: 'Speak with grace. Encourage one another, never tear down.' },
  { title: 'No spam or unsolicited links', description: 'No advertising, referral links, or flooding the chat.' },
  { title: 'Keep it clean', description: 'No vulgar language, harassment, or harmful content.' },
  { title: 'Verify yourself', description: 'Complete the captcha check to join the conversation.' },
  { title: 'Stay on topic', description: 'Keep fellowship and Bible discussion in their proper spaces.' },
  { title: 'Respect the team', description: 'Follow moderator guidance, and appeal calmly if you disagree.' },
];
