import React, { useEffect, useState } from 'react';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchLeaderboard, type LeaderboardItem } from '../../services/api';

interface QuizTabProps {
  profile: ProfileState;
}

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 4px 0', color: '#0f172a' }}>
          Quiz & Gamification Hub
        </h2>
        <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
          Powered by Lusy Bot &bull; 4 Interactive Quiz Modes & YP Rewards
        </p>
      </div>

      {/* User Rank & XP Progress Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '14px',
          padding: '18px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Your Rank Status
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#6d28d9', marginTop: '2px' }}>
              {p ? `Level ${p.level}` : 'Level 1'}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Earned
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>
              {p ? `${p.totalXp} XP` : '0 XP'}
            </div>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div style={{ width: '100%', height: '8px', backgroundColor: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
          <div
            style={{
              width: p ? `${Math.min(100, (p.totalXp % 500) / 5)}%` : '15%',
              height: '100%',
              backgroundColor: '#6d28d9',
              borderRadius: '4px',
            }}
          />
        </div>
      </div>

      {/* Live Community Leaderboard Section */}
      <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '18px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0, color: '#0f172a' }}>
            Top Community Leaderboard
          </h3>
          <span style={{ fontSize: '11px', color: '#6d28d9', fontWeight: 600 }}>Top 10</span>
        </div>

        {loadingLeaderboard ? (
          <div style={{ fontSize: '12px', color: '#64748b' }}>Loading community rankings…</div>
        ) : leaderboard.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {leaderboard.map((item, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 10px',
                  backgroundColor: idx === 0 ? '#faf5ff' : '#f8fafc',
                  border: '1px solid #f1f5f9',
                  borderRadius: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 800, color: idx === 0 ? '#6d28d9' : '#64748b', width: '18px' }}>
                    #{idx + 1}
                  </span>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>
                    {item.displayName || 'Anonymous Member'}
                  </span>
                </div>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#6d28d9' }}>
                  {item.totalXp} XP (Lvl {item.level})
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ fontSize: '12px', color: '#64748b' }}>No leaderboard records yet. Play quizzes with Lusy to earn XP!</div>
        )}
      </div>

      {/* 4 Lusy Quiz Modes */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <h3 style={{ fontSize: '14px', fontWeight: 700, margin: 0, color: '#0f172a' }}>
          Available Quiz Modes (4)
        </h3>

        {quizModes.map((quiz) => (
          <div
            key={quiz.id}
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '14px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>{quiz.title}</div>
              <div style={{ fontSize: '11px', fontWeight: 500, color: '#6d28d9', marginTop: '1px' }}>{quiz.subtitle}</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>{quiz.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
