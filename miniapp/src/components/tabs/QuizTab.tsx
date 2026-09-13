import React, { useEffect, useState } from 'react';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchLeaderboard, type LeaderboardItem } from '../../services/api';
import { Card, Skeleton, SectionTitle, Pill, ProgressBar } from '../ui';
import { RankBadge } from '../RankBadge';

interface QuizTabProps {
  profile: ProfileState;
}

const MEDALS: Record<number, { bg: string; color: string; label: string }> = {
  0: { bg: '#fef3c7', color: '#b45309', label: '🥇' },
  1: { bg: '#f1f5f9', color: '#475569', label: '🥈' },
  2: { bg: '#fed7aa', color: '#9a3412', label: '🥉' },
};

export const QuizTab: React.FC<QuizTabProps> = ({ profile }) => {
  const p = profile.status === 'ok' ? profile.profile : null;
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [loadingLeaderboard, setLoadingLeaderboard] = useState<boolean>(true);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const items = await fetchLeaderboard();
      if (!cancelled) {
        setLeaderboard(items);
        setLoadingLeaderboard(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const quizModes = [
    {
      id: 'challenge',
      title: 'Bible Challenge',
      subtitle: 'Multiple Choice Trivia',
      description: 'Test your foundational Bible knowledge across classic multiple choice questions.',
      tag: 'Classic',
    },
    {
      id: 'completion',
      title: 'Verse Completion',
      subtitle: 'Fill-in-the-Blank',
      description: 'Identify and fill in missing keywords in sacred Scripture passages.',
      tag: 'Memory',
    },
    {
      id: 'scramble',
      title: 'Verse Scramble',
      subtitle: 'Word Ordering',
      description: 'Unscramble shuffled Scripture words into their correct biblical sequence.',
      tag: 'Puzzle',
    },
    {
      id: 'race',
      title: 'Trivia Race',
      subtitle: 'Rapid Timed Competition',
      description: 'Compete against the clock in a fast-paced Bible speed challenge.',
      tag: 'Speed',
    },
  ];

  return (
    <div className="section-stack">
      {/* Lusy Gaming Hero Banner */}
      <section
        style={{
          borderRadius: 28,
          padding: 20,
          color: '#ffffff',
          background: 'var(--grad-quiz)',
          boxShadow: 'var(--shadow-purple)',
        }}
      >
        <Pill color="deep" style={{ background: 'rgba(255,255,255,0.16)', borderColor: 'rgba(255,255,255,0.26)', marginBottom: 12 }}>
          Lusy Gaming Hub
        </Pill>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="eyebrow" style={{ color: 'rgba(255,255,255,0.85)', marginBottom: 3 }}>Your Rank Status</div>
            <div style={{ fontSize: 24, fontWeight: 900, marginTop: 2, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span>Level {p ? p.level : 1}</span>
              {p?.rankTitle && (
                <RankBadge
                  title={p.rankTitle}
                  emoji={p.rankEmoji}
                  color={p.rankBadgeColor}
                  size="sm"
                />
              )}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="eyebrow" style={{ color: 'rgba(255,255,255,0.85)', marginBottom: 3 }}>Total XP</div>
            <div style={{ fontSize: 22, fontWeight: 900, marginTop: 2 }}>{p ? `${p.totalXp.toLocaleString()} XP` : '0 XP'}</div>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div style={{ marginTop: 18 }}>
          <ProgressBar value={p ? p.totalXp % 500 : 75} max={500} tone="purple" />
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.85)', marginTop: 8 }}>
            {p ? `${500 - (p.totalXp % 500)} XP to Level ${p.level + 1}` : 'Play quizzes with Lusy to earn XP'}
          </div>
        </div>

        {/* Live Quiz Stats */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 10,
            marginTop: 16,
            paddingTop: 16,
            borderTop: '1px solid rgba(255,255,255,0.15)',
          }}
        >
          <div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)' }}>Quizzes Completed</div>
            <div style={{ fontSize: 16, fontWeight: 850, marginTop: 2 }}>{p?.quizzesPlayed ?? 0} Played</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)' }}>Quiz Accuracy</div>
            <div style={{ fontSize: 16, fontWeight: 850, marginTop: 2 }}>{p?.accuracyPct ?? 100}%</div>
          </div>
        </div>
      </section>

      {/* Live Community Leaderboard Section */}
      <Card style={{ padding: 18 }} hover>
        <SectionTitle right={<Pill color="purple">Top 10</Pill>}>Global Leaderboard</SectionTitle>

        {loadingLeaderboard ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[0, 1, 2, 3].map((i) => (
              <Skeleton key={i} height={40} radius={10} />
            ))}
          </div>
        ) : leaderboard.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {leaderboard.map((item, idx) => {
              const medal = MEDALS[idx];
              const isTop3 = medal !== undefined;

              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: isTop3 ? medal.bg : 'var(--surface-soft)',
                    border: '1px solid var(--slate-100)',
                    gap: 8,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <span
                      style={{
                        fontSize: 12,
                        fontWeight: 700,
                        color: isTop3 ? medal.color : 'var(--text-muted)',
                        width: 24,
                      }}
                    >
                      {isTop3 ? medal.label : `#${idx + 1}`}
                    </span>
                    <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-color)' }}>
                      {item.displayName || 'Anonymous Member'}
                    </span>
                    {item.rankTitle && (
                      <RankBadge
                        title={item.rankTitle}
                        emoji={item.rankEmoji}
                        color={item.rankBadgeColor}
                        size="sm"
                      />
                    )}
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--primary-purple)', whiteSpace: 'nowrap' }}>
                    {item.totalXp.toLocaleString()} XP (Lvl {item.level})
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            No leaderboard records yet. Play quizzes with Lusy to earn XP!
          </div>
        )}
      </Card>

      {/* 4 Lusy Quiz Modes */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <SectionTitle eyebrow="Game Arena" right={<Pill color="purple">4 Modes</Pill>}>
          Available Quiz Modes
        </SectionTitle>

        {quizModes.map((quiz) => (
          <Card key={quiz.id} hover style={{ padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-color)' }}>{quiz.title}</span>
                  <Pill color="neutral">{quiz.tag}</Pill>
                </div>
                <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--primary-purple)', marginBottom: 4 }}>{quiz.subtitle}</div>
                <div className="muted-copy" style={{ fontSize: 12 }}>{quiz.description}</div>
              </div>
              <a
                href="https://t.me/iamlusybot?start=playquiz"
                target="_blank"
                rel="noreferrer"
                className="ghost-button"
                style={{ textDecoration: 'none', height: 34, minHeight: 34, fontSize: 12, padding: '0 14px', flexShrink: 0 }}
              >
                Play →
              </a>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
