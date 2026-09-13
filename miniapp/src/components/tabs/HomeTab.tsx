import React, { useEffect, useState } from 'react';
import type { TelegramUser } from '../../types/telegram';
import type { TabId } from '../../types/navigation';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchVotd, type VotdItem } from '../../services/api';
import { Card, Pill, ProgressBar, SectionTitle, Skeleton } from '../ui';
import { RankBadge } from '../RankBadge';

interface HomeTabProps {
  user: TelegramUser | null;
  profile: ProfileState;
  verified: boolean;
  onNavigate: (tab: TabId) => void;
}

export const HomeTab: React.FC<HomeTabProps> = ({ user, profile, verified, onNavigate }) => {
  const profileData = profile.status === 'ok' ? profile.profile : null;
  const [votd, setVotd] = useState<VotdItem | null>(null);
  const [loadingVotd, setLoadingVotd] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const item = await fetchVotd('KJV');
      if (!cancelled) {
        setVotd(item);
        setLoadingVotd(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const firstName = user?.firstName?.split(' ')[0] || 'Friend';
  const xp = profileData?.totalXp ?? 0;
  const level = profileData?.level ?? 1;
  const nextLevelProgress = Math.min(100, xp % 500 === 0 && xp > 0 ? 100 : (xp % 500) / 5);

  return (
    <div className="section-stack">
      <section
        style={{
          position: 'relative',
          overflow: 'hidden',
          borderRadius: 28,
          padding: 20,
          color: '#fff',
          background: 'var(--grad-hero)',
          boxShadow: 'var(--shadow-purple)',
        }}
      >
        <div style={{ position: 'absolute', top: -52, right: -40, width: 150, height: 150, borderRadius: '50%', background: 'rgba(255,255,255,0.1)' }} />
        <div style={{ position: 'absolute', bottom: -78, left: -20, width: 160, height: 160, borderRadius: '50%', background: 'rgba(255,255,255,0.08)' }} />

        <div style={{ position: 'relative' }}>
          <Pill color="deep" style={{ background: 'rgba(255,255,255,0.16)', borderColor: 'rgba(255,255,255,0.26)', marginBottom: 14 }}>
            {verified ? 'Verified member' : 'Telegram member'}
          </Pill>
          <h2 style={{ margin: 0, fontSize: 28, lineHeight: 1.06, fontWeight: 950 }}>
            Welcome back, {firstName}
          </h2>
          <p style={{ margin: '8px 0 0', maxWidth: 320, color: 'rgba(255,255,255,0.82)', fontSize: 13, lineHeight: 1.55 }}>
            Your daily hub for Scripture, challenges, events, and community progress.
          </p>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginTop: 20 }}>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 11, fontWeight: 800, opacity: 0.72, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Current standing</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginTop: 5 }}>
                <span style={{ fontSize: 25, fontWeight: 950 }}>Level {level}</span>
                {profileData?.rankTitle && (
                  <RankBadge title={profileData.rankTitle} emoji={profileData.rankEmoji} color={profileData.rankBadgeColor} size="sm" />
                )}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 11, fontWeight: 800, opacity: 0.72, textTransform: 'uppercase', letterSpacing: '0.08em' }}>XP</div>
              <div style={{ fontSize: 24, fontWeight: 950 }}>{xp.toLocaleString()}</div>
            </div>
          </div>

          <div style={{ marginTop: 16 }}>
            <ProgressBar value={nextLevelProgress} />
            <div style={{ marginTop: 8, color: 'rgba(255,255,255,0.75)', fontSize: 11, fontWeight: 700 }}>
              {Math.round(nextLevelProgress)}% toward your next level
            </div>
          </div>
        </div>
      </section>

      <div className="metric-grid">
        <div className="metric-tile">
          <div className="metric-label">Trust</div>
          <div className="metric-value">{profileData?.trustScore ?? 100}</div>
        </div>
        <div className="metric-tile">
          <div className="metric-label">Quizzes</div>
          <div className="metric-value">{profileData?.quizzesPlayed ?? 0}</div>
        </div>
        <div className="metric-tile">
          <div className="metric-label">Accuracy</div>
          <div className="metric-value">{profileData?.accuracyPct ?? 100}%</div>
        </div>
      </div>

      <Card style={{ padding: 18 }} hover>
        <SectionTitle eyebrow="Theo Daily Focus" right={<Pill color="purple">{votd?.translation || 'KJV'}</Pill>}>
          Verse of the Day
        </SectionTitle>

        {loadingVotd ? (
          <div style={{ display: 'grid', gap: 9 }}>
            <Skeleton height={15} />
            <Skeleton height={15} width="86%" />
            <Skeleton height={12} width="42%" />
          </div>
        ) : (
          <div>
            <p style={{ margin: 0, color: 'var(--text-color)', fontSize: 16, lineHeight: 1.75, fontWeight: 550 }}>
              "{votd?.text}"
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginTop: 14 }}>
              <strong style={{ color: 'var(--primary-purple)', fontSize: 13 }}>{votd?.reference}</strong>
              <button className="ghost-button" onClick={() => onNavigate('bible')}>Open Bible</button>
            </div>
          </div>
        )}
      </Card>

      <Card style={{ padding: 18, background: 'linear-gradient(135deg,#ffffff,#faf7ff)' }}>
        <SectionTitle eyebrow="Today" right={<Pill color="warning">AOTD soon</Pill>}>
          Daily Rhythm
        </SectionTitle>
        <div style={{ display: 'grid', gap: 10 }}>
          {([
            { title: 'Scripture', copy: 'Read the daily verse and save what speaks to you.', tab: 'bible' as TabId },
            { title: 'Challenge', copy: 'Play one Lusy Bible challenge and keep your XP moving.', tab: 'quiz' as TabId },
            { title: 'Gathering', copy: 'Check the next Eddy event or reminder.', tab: 'events' as TabId },
          ] as const).map(({ title, copy, tab }) => (
            <button
              key={title}
              onClick={() => onNavigate(tab)}
              style={{
                width: '100%',
                border: '1px solid var(--purple-100)',
                borderRadius: 'var(--radius-lg)',
                background: '#fff',
                padding: 13,
                textAlign: 'left',
                cursor: 'pointer',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                <strong style={{ color: 'var(--text-color)', fontSize: 14 }}>{title}</strong>
                <span style={{ color: 'var(--primary-purple)', fontWeight: 900 }}>→</span>
              </div>
              <div className="muted-copy" style={{ marginTop: 3 }}>{copy}</div>
            </button>
          ))}
        </div>
      </Card>
    </div>
  );
};
