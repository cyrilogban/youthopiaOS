export interface AssistantEntry {
  /** Formal given name, e.g. Theodore. */
  formal: string;
  /** Short display name used across the app, e.g. Theo. */
  short: string;
  handle: string;
  emoji: string;
  responsibility: string;
  link: string;
}

export const ASSISTANTS: AssistantEntry[] = [
  {
    formal: 'Theodore',
    short: 'Theo',
    handle: '@theobiblebot',
    emoji: '📖',
    responsibility: 'Scripture, devotionals, saved verses, and theological assistance',
    link: 'https://t.me/theobiblebot',
  },
  {
    formal: 'Lucy',
    short: 'Lusie',
    handle: '@lusiequizbot',
    emoji: '🎯',
    responsibility: 'Bible quizzes, XP, competitions, and leaderboards',
    link: 'https://t.me/lusiequizbot',
  },
  {
    formal: 'Edmund',
    short: 'Edie',
    handle: '@ediecalendarbot',
    emoji: '📅',
    responsibility: 'Calendar, events, meetings, birthdays, and reminders',
    link: 'https://t.me/ediecalendarbot',
  },
  {
    formal: 'Peter',
    short: 'Pete',
    handle: '@petemodbot',
    emoji: '🛡️',
    responsibility: 'Moderation, anti-spam, and community safety',
    link: 'https://t.me/petemodbot',
  },
  {
    formal: 'Susan',
    short: 'Susie',
    handle: '@susiehelpsbot',
    emoji: '💬',
    responsibility: 'Onboarding, welcome, and hospitality',
    link: 'https://t.me/susiehelpsbot',
  },
];

export interface CommunitySpace {
  name: string;
  role: string;
  link: string;
}

export const COMMUNITY_SPACES: CommunitySpace[] = [
  { name: 'Telegram Community', role: 'Main fellowship group for general fellowship, announcements, and support', link: 'https://t.me/youthopiabiblecommunity' },
  { name: 'WhatsApp Community', role: 'Daily encouragement and conversation on WhatsApp', link: 'https://chat.whatsapp.com/HXZsnWjwizoHBojS2VwbHn' },
  { name: 'Facebook Community', role: 'Fellowship and community updates on Facebook', link: 'https://www.facebook.com/share/g/18wG8aWB6t/' },
];

export interface FaqEntry {
  question: string;
  answer: string;
}

export const FAQS: FaqEntry[] = [
  {
    question: 'What is YouThopia Bible Community?',
    answer: 'YouThopia Bible Community is a digital fellowship of believers dedicated to studying Scripture, deepening faith, playing and learning together, and sharing God\'s love all the way.',
  },
  {
    question: 'What is YouThopiaOS?',
    answer: 'YouThopiaOS is the software engine powering our five Telegram assistants (Theodore, Lucy, Edmund, Peter, Susan) and this unified Mini App.',
  },
  {
    question: 'How do I earn XP and level up?',
    answer: 'You earn YouTopian Points by taking quizzes with Lusie and completing Scripture challenges. Your XP follows you across every part of the community.',
  },
  {
    question: 'How does verification work?',
    answer: 'When you open the Mini App inside Telegram, your signed Telegram identity is verified server-side before your profile is shown.',
  },
  {
    question: 'What is the Trust Score?',
    answer: 'Pete maintains a Trust Score out of 100 for every member, based on verification, clean interactions, and account standing.',
  },
  {
    question: 'How do I get oriented?',
    answer: 'Take the YouThopia Tour with Susie. It walks you through our mission, vision, and the five pillars, and finishing it marks you oriented and claims your one-time welcome boost.',
  },
];

export interface OnboardingStep {
  step: string;
  title: string;
  description: string;
  /** Route to visit to complete this step, when it lives in another bot's space. */
  route?: string;
  /** Where the step happens, shown as a hint. */
  space: string;
}

export const ONBOARDING_STEPS: OnboardingStep[] = [
  { step: '01', title: 'Meet your hostess', description: 'Say hello to Susie and get a feel for the community.', space: 'Susie', route: undefined },
  { step: '02', title: 'Take the YouThopia Tour', description: 'The guided tour of our mission, vision, and the five pillars (+50 Trust).', space: 'Susie' },
  { step: '03', title: 'Set your Bible preferences', description: 'Choose your default Scripture translation and daily verse.', space: 'Theo', route: '/theo/profile' },
  { step: '04', title: 'Take your first quiz', description: 'Answer questions with Lusie to start earning YouTopian Points.', space: 'Lusie', route: '/lusie' },
  { step: '05', title: 'Join a gathering', description: 'RSVP for a weekly study or prayer call with Edie.', space: 'Edie', route: '/edie' },
];
