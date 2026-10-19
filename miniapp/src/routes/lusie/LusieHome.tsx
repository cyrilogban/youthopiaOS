import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppData } from '../../context/AppData';
import { Card, Pill, ProgressBar, SectionTitle } from '../../components/ui';
import { RankBadge } from '../../components/RankBadge';
import { GAME_MODES } from '../../data/games';

const lusieLink = (payload: string) => `https://t.me/lusiequizbot?start=${payload}`;

export const LusieHome: React.FC = () => {
  const navigate = useNavigate();
  const { profile } = useAppData();
  const member = profile.status === 'ok' ? profile.profile : null;
  const xp = member?.totalXp ?? 0;
  const level = member?.level && member.level > 1 ? member.level : Math.max(1, Math.floor(xp / 100) + 1);
  const progress = xp % 100;

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Learn the Word by playing.</h1>
        <p>I'm Lusie. Take a small challenge, build your confidence, and earn points that follow you across YouThopia.</p>
      </section>

      <Card style={{ padding: 20, background: 'var(--grad-quiet)', borderColor: 'var(--purple-200)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start' }}>
          <div>
            <div className="eyebrow">Your play status</div>
            <div style={{ marginTop: 5, fontSize: 28, fontWeight: 800 }}>Level {level}</div>
            {member?.rankTitle && (
              <div style={{ marginTop: 8 }}>
                <RankBadge title={member.rankTitle} emoji={member.rankEmoji} color={member.rankBadgeColor} size="sm" />
              </div>
            )}
          </div>
          <div style={{ textAlign: 'right' }}>
            <strong style={{ display: 'block', fontSize: 20 }}>{xp.toLocaleString()}</strong>
            <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>total XP</span>
          </div>
        </div>
        <div style={{ marginTop: 18 }}>
          <ProgressBar value={progress} max={100} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, color: 'var(--text-secondary)', fontSize: 11 }}>
          <span>{member?.quizzesPlayed ?? 0} quizzes played</span>
          <span>{member?.accuracyPct ?? 100}% accuracy</span>
        </div>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Start here" right={<Pill color="purple">Featured</Pill>}>Today's challenge</SectionTitle>
        <Card style={{ padding: 20, borderColor: 'var(--purple-200)' }}>
          <div className="eyebrow">Bible Challenge</div>
          <h2 style={{ margin: '6px 0 0', fontSize: 21 }}>Five questions. One stronger foundation.</h2>
          <p className="muted-copy" style={{ marginTop: 8 }}>Open Lusie for a focused round and earn XP for every correct answer.</p>
          <a className="primary-button" href={lusieLink('playquiz')} target="_blank" rel="noreferrer" style={{ marginTop: 16 }}>
            Start challenge
          </a>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Your game room" right={<Pill color="slate">{GAME_MODES.length} modes</Pill>}>Where to go</SectionTitle>
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'grid', gap: 10 }}>
            <button className="secondary-button" onClick={() => navigate('/lusie/play')} style={{ width: '100%' }}>
              Play a mode
            </button>
            <button className="secondary-button" onClick={() => navigate('/lusie/leaderboard')} style={{ width: '100%' }}>
              See the leaderboard
            </button>
            <button className="secondary-button" onClick={() => navigate('/lusie/profile')} style={{ width: '100%' }}>
              View my player profile
            </button>
          </div>
        </Card>
      </section>
    </div>
  );
};
