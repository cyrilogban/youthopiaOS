import React, { useEffect, useState } from 'react';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchLeaderboard, type LeaderboardItem } from '../../services/api';
import { Card, Skeleton, SectionTitle, Pill } from '../ui';

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
    },
    {
      id: 'completion',
      title: 'Verse Completion',
      subtitle: 'Fill-in-the-Blank',
      description: 'Identify and fill in missing keywords in sacred Scripture passages.',
    },
    {
      id: 'scramble',
      title: 'Verse Scramble',
      subtitle: 'Word Ordering',
      description: 'Unscramble shuffled Scripture words into their correct biblical sequence.',
    },
    {
      id: 'race',
      title: 'Trivia Race',
      subtitle: 'Rapid Timed Competition',
      description: 'Compete against the clock in a fast-paced Bible speed challenge.',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-color)', letterSpacing: '-0.02em' }}>
          Quiz & Gamification Hub
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
          Powered by Lusy Bot &bull; 4 Interactive Quiz Modes & YP Rewards
        </p>
      </div>

      {/* User Rank & XP Progress Card */}
      <div
        style={{
          background: 'var(--grad-quiz)',
          borderRadius: 'var(--radius-xl)',
          padding: 20,
          color: '#ffffff',
          boxShadow: '0 10px 28px rgba(76, 29, 149, 0.3)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontSize: 11, opacity: 0.85, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Your Rank Status</div>
            <div style={{ fontSize: 28, fontWeight: 800, marginTop: 2 }}>{p ? `Level ${p.level}` : 'Level 1'}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, opacity: 0.85, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Total Earned</div>
            <div style={{ fontSize: 24, fontWeight: 800, marginTop: 2 }}>{p ? `${p.totalXp.toLocaleString()} XP` : '0 XP'}</div>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div style={{ marginTop: 18 }}>
          <div style={{ width: '100%', height: 10, background: 'rgba(255,255,255,0.2)', borderRadius: 5, overflow: 'hidden' }}>
            <div
              style={{
                width: p ? `${Math.min(100, (p.totalXp % 500) / 5)}%` : '15%',
                height: '100%',
                background: 'linear-gradient(90deg,#e9d5ff,#ffffff)',
                borderRadius: 5,
                transition: 'width 0.9s var(--ease)',
              }}
            />
          </div>
          <div style={{ fontSize: 11, opacity: 0.85, marginTop: 8 }}>Earn XP toward the next level</div>
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
            <div style={{ fontSize: 11, opacity: 0.85 }}>Quizzes Completed</div>
            <div style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>{p?.quizzesPlayed ?? 0} Played</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, opacity: 0.85 }}>Quiz Accuracy</div>
            <div style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>{p?.accuracyPct ?? 100}%</div>
          </div>
        </div>
      </div>

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
                    background: isTop3 ? medal.bg : 'var(--surface-soft)',
                    border: '1px solid var(--slate-100)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span
                      style={{
                        fontSize: 12,
                        fontWeight: 800,
                        color: isTop3 ? medal.color : 'var(--text-muted)',
                        width: 30,
                      }}
                    >
                      {isTop3 ? medal.label : `#${idx + 1}`}
                    </span>
                    <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-color)' }}>
                      {item.displayName || 'Anonymous Member'}
                    </span>
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--primary-purple)' }}>
                    {item.totalXp} XP (Lvl {item.level})
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
        <SectionTitle>Available Quiz Modes (4)</SectionTitle>

        {quizModes.map((quiz) => (
          <Card key={quiz.id} hover style={{ padding: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-color)' }}>{quiz.title}</div>
              <div style={{ fontSize: 11, fontWeight: 500, color: 'var(--primary-purple)', marginTop: 1 }}>{quiz.subtitle}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4, lineHeight: 1.5 }}>{quiz.description}</div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
