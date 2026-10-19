export interface GameMode {
  title: string;
  description: string;
  reward: string;
  /** Deep-link payload for Lusie, e.g. playquiz -> ?start=playquiz */
  path: string;
}

export const GAME_MODES: GameMode[] = [
  { title: 'Bible Challenge', description: 'A multiple-choice round to test what you know.', reward: 'Up to 40 XP', path: 'playquiz' },
  { title: 'Verse Completion', description: 'Finish the verse and remember it for good.', reward: 'Up to 50 XP', path: 'versecompletion' },
  { title: 'Verse Scramble', description: 'Put Scripture back in the right order.', reward: 'Up to 50 XP', path: 'scramble' },
  { title: 'Trivia Race', description: 'A rapid round when you want a quick challenge.', reward: 'Speed round', path: 'triviarace' },
];
