import React, { useEffect, useState } from 'react';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchLeaderboard, type LeaderboardItem } from '../../services/api';
import { Card, Pill, ProgressBar, SectionTitle, Skeleton } from '../ui';
import { RankBadge } from '../RankBadge';

interface QuizTabProps { profile: ProfileState; }

const GAME_MODES = [
  { title: 'Bible Challenge', description: 'A multiple-choice round to test what you know.', reward: 'Up to 40 XP', path: 'playquiz' },
  { title: 'Verse Completion', description: 'Finish the verse and train your memory.', reward: 'Up to 50 XP', path: 'versecompletion' },
  { title: 'Verse Scramble', description: 'Put Scripture back in the right order.', reward: 'Up to 50 XP', path: 'scramble' },
  { title: 'Trivia Race', description: 'A rapid round when you want a quick challenge.', reward: 'Speed round', path: 'triviarace' },
];

export const QuizTab: React.FC<QuizTabProps> = ({ profile }) => {
  const member = profile.status === 'ok' ? profile.profile : null;
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const xp = member?.totalXp ?? 0;
  const level = member?.level && member.level > 1 ? member.level : Math.max(1, Math.floor(xp / 100) + 1);
  const progress = xp % 100;

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const members = await fetchLeaderboard();
      if (!cancelled) {
        setLeaderboard(members);
        setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">Lusie's game room</span>
        <h1>Learn the Word by playing.</h1>
        <p>Take a small challenge, build your confidence, and earn progress that follows you across YouThopia.</p>
      </section>

      <Card style={{ padding: 20, background: 'var(--grad-quiet)', borderColor: 'var(--purple-200)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start' }}>
          <div>
            <div className="eyebrow">Your play status</div>
            <div style={{ marginTop: 5, fontSize: 28, fontWeight: 800 }}>Level {level}</div>
            {member?.rankTitle && <div style={{ marginTop: 8 }}><RankBadge title={member.rankTitle} emoji={member.rankEmoji} color={member.rankBadgeColor} size="sm" /></div>}
          </div>
          <div style={{ textAlign: 'right' }}><strong style={{ display: 'block', fontSize: 20 }}>{xp.toLocaleString()}</strong><span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>total XP</span></div>
        </div>
        <div style={{ marginTop: 18 }}><ProgressBar value={progress} max={100} /></div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, color: 'var(--text-secondary)', fontSize: 11 }}><span>{member?.quizzesPlayed ?? 0} quizzes played</span><span>{member?.accuracyPct ?? 100}% accuracy</span></div>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Start here" right={<Pill color="purple">Featured</Pill>}>Today's challenge</SectionTitle>
        <Card style={{ padding: 20, borderColor: 'var(--purple-200)' }}>
          <div className="eyebrow">Bible Challenge</div>
          <h2 style={{ margin: '6px 0 0', fontSize: 21 }}>Five questions. One stronger foundation.</h2>
          <p className="muted-copy" style={{ marginTop: 8 }}>Open Lusie for a focused Bible quiz round and earn XP for every correct answer.</p>
          <a className="primary-button" href="https://t.me/lusiequizbot?start=playquiz" target="_blank" rel="noreferrer" style={{ marginTop: 16 }}>Start challenge</a>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Choose a mode">Play your way</SectionTitle>
        <div style={{ display: 'grid', gap: 10 }}>
          {GAME_MODES.map((game) => (
            <Card key={game.path} style={{ padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <strong style={{ fontSize: 15 }}>{game.title}</strong>
                  <p className="muted-copy" style={{ marginTop: 4 }}>{game.description}</p>
                  <Pill color="slate" style={{ marginTop: 10 }}>{game.reward}</Pill>
                </div>
                <a className="secondary-button" href={`https://t.me/lusiequizbot?start=${game.path}`} target="_blank" rel="noreferrer" style={{ minHeight: 36, paddingInline: 13 }}>Open</a>
              </div>
            </Card>
          ))}
        </div>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Community" right={<Pill color="slate">Top 10</Pill>}>Leaderboard</SectionTitle>
        <Card style={{ padding: 10 }}>
          {loading ? (
            <div style={{ display: 'grid', gap: 8, padding: 6 }}>{[1, 2, 3].map((item) => <Skeleton key={item} height={46} />)}</div>
          ) : leaderboard.length ? (
            <div style={{ display: 'grid', gap: 3 }}>
              {leaderboard.slice(0, 5).map((item, index) => (
                <div key={`${item.displayName}-${index}`} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 8px', borderBottom: index < 4 ? '1px solid var(--slate-100)' : undefined }}>
                  <strong style={{ width: 24, color: 'var(--primary-purple)', fontSize: 12 }}>#{index + 1}</strong>
                  <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 13, fontWeight: 700 }}>{item.displayName || 'Community member'}</span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 700 }}>{item.totalXp.toLocaleString()} XP</span>
                </div>
              ))}
            </div>
          ) : <p className="muted-copy" style={{ padding: 12 }}>The leaderboard will grow as members begin playing.</p>}
        </Card>
      </section>
    </div>
  );
};
