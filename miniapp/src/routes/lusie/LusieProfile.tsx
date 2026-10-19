import React from 'react';
import { useAppData } from '../../context/AppData';
import { Card, Pill, ProgressBar, SectionTitle } from '../../components/ui';
import { RankBadge } from '../../components/RankBadge';

export const LusieProfile: React.FC = () => {
  const { user, profile } = useAppData();
  const member = profile.status === 'ok' ? profile.profile : null;
  const xp = member?.totalXp ?? 0;
  const level = member?.level && member.level > 1 ? member.level : Math.max(1, Math.floor(xp / 100) + 1);
  const progress = xp % 100;
  const displayName = user?.firstName || member?.displayName || 'Player';
  const initial = displayName[0]?.toUpperCase() || 'Y';

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>{displayName}</h1>
        <p>Your player card, and the progress you have earned so far.</p>
      </section>

      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span className="profile-avatar" style={{ width: 58, height: 58, fontSize: 20 }}>
            {user?.photoUrl ? <img src={user.photoUrl} alt={displayName} /> : initial}
          </span>
          <div style={{ display: 'grid', gap: 8 }}>
            {member?.rankTitle && (
              <RankBadge title={member.rankTitle} emoji={member.rankEmoji} color={member.rankBadgeColor} size="md" />
            )}
            <Pill color="purple">Level {level}</Pill>
          </div>
        </div>

        <div style={{ marginTop: 18 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <span className="metric-label">Progress to next level</span>
            <strong style={{ fontSize: 14 }}>{progress}%</strong>
          </div>
          <div style={{ marginTop: 8 }}>
            <ProgressBar value={progress} max={100} />
          </div>
        </div>

        <div className="metric-grid" style={{ marginTop: 20 }}>
          <div className="metric-tile">
            <div className="metric-label">Total XP</div>
            <div className="metric-value">{xp.toLocaleString()}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-label">Quizzes</div>
            <div className="metric-value">{member?.quizzesPlayed ?? 0}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-label">Accuracy</div>
            <div className="metric-value">{member?.accuracyPct ?? 100}%</div>
          </div>
        </div>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Keep going" right={<Pill color="purple">Earn XP</Pill>}>Build your rank</SectionTitle>
        <Card style={{ padding: 16 }}>
          <p className="muted-copy" style={{ margin: 0 }}>
            Every quiz you play adds to your XP and lifts your rank. Play a mode with Lusie whenever you have a
            few minutes, and watch your card grow.
          </p>
        </Card>
      </section>

      <a className="secondary-button" href="https://t.me/lusiequizbot" target="_blank" rel="noreferrer" style={{ width: '100%' }}>
        Open Lusie in Telegram
      </a>
    </div>
  );
};
