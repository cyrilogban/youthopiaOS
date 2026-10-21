import React, { useEffect, useState } from 'react';
import type { TelegramUser } from '../../types/telegram';
import type { TabId } from '../../types/navigation';
import type { ProfileState } from '../../hooks/useTelegram';
import { fetchEvents, fetchVotd, type EventItem, type VotdItem } from '../../services/api';
import { Card, Pill, ProgressBar, SectionTitle, Skeleton } from '../ui';
import { RankBadge } from '../RankBadge';
import { BotSwitcherSheet } from '../BotSwitcherSheet';

interface HomeTabProps {
  user: TelegramUser | null;
  profile: ProfileState;
  verified: boolean;
  onNavigate: (tab: TabId) => void;
}

export const HomeTab: React.FC<HomeTabProps> = ({ user, profile, verified, onNavigate }) => {
  const profileData = profile.status === 'ok' ? profile.profile : null;
  const [votd, setVotd] = useState<VotdItem | null>(null);
  const [event, setEvent] = useState<EventItem | null>(null);
  const [loadingVotd, setLoadingVotd] = useState(true);
  const [switchOpen, setSwitchOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const [verse, events] = await Promise.all([fetchVotd('KJV'), fetchEvents()]);
      if (!cancelled) {
        setVotd(verse);
        setEvent(events[0] ?? null);
        setLoadingVotd(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const firstName = user?.firstName?.split(' ')[0] || 'Friend';
  const totalXp = profileData?.totalXp ?? 0;
  const level = profileData?.level && profileData.level > 1 ? profileData.level : Math.max(1, Math.floor(totalXp / 100) + 1);
  const progress = totalXp % 100;
  const toNextLevel = 100 - progress;

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">{verified ? 'Your community is ready' : 'Welcome to YouThopia Bible Community'}</span>
        <h1>Good day, {firstName}.</h1>
        <p>Start with the Word, carry one thought with you, and stay close to your community.</p>
      </section>

      {loadingVotd ? (
        <div className="editorial-card"><Skeleton height={12} width="34%" /><Skeleton height={28} style={{ marginTop: 18 }} /><Skeleton height={28} width="84%" style={{ marginTop: 9 }} /></div>
      ) : (
        <section className="editorial-card">
          <div className="eyebrow">Today's Scripture</div>
          <p>“{votd?.text}”</p>
          <footer>
            <span>{votd?.reference}</span>
            <button onClick={() => onNavigate('bible')} className="secondary-button" style={{ minHeight: 44, color: '#fff', background: 'rgba(255,255,255,0.14)', borderColor: 'rgba(255,255,255,0.35)' }}>Read in Word</button>
          </footer>
        </section>
      )}

      <section className="section-group">
        <SectionTitle eyebrow="Your growth" right={<Pill color="purple">Level {level}</Pill>}>One small step today</SectionTitle>
        <Card style={{ padding: 18 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start' }}>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>YouTopian points</div>
              <div style={{ marginTop: 4, fontSize: 28, fontWeight: 800 }}>{totalXp.toLocaleString()} XP</div>
              {profileData?.rankTitle && <div style={{ marginTop: 8 }}><RankBadge title={profileData.rankTitle} emoji={profileData.rankEmoji} color={profileData.rankBadgeColor} size="sm" /></div>}
            </div>
            <div style={{ textAlign: 'right', color: 'var(--text-secondary)', fontSize: 12 }}>
              <strong style={{ display: 'block', color: 'var(--ink)', fontSize: 16 }}>{toNextLevel} XP</strong>
              to Level {level + 1}
            </div>
          </div>
          <div style={{ marginTop: 18 }}><ProgressBar value={progress} max={100} /></div>
          <button className="primary-button" onClick={() => onNavigate('quiz')} style={{ width: '100%', marginTop: 18 }}>Play today's challenge</button>
        </Card>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Keep moving">Your next moment</SectionTitle>
        <button className="feature-row" onClick={() => onNavigate('events')}>
          <span style={{ minWidth: 0 }}>
            <strong>{event?.title ?? 'See what is happening this week'}</strong>
            <span>{event ? `${event.startsAt} · ${event.location ?? 'YouThopia'}` : 'View upcoming gatherings and reminders.'}</span>
          </span>
          <span className="feature-row-arrow">→</span>
        </button>
        <button className="feature-row" onClick={() => onNavigate('community')}>
          <span style={{ minWidth: 0 }}>
            <strong>Find your place in the community</strong>
            <span>Meet the assistants, find answers, and manage your community settings.</span>
          </span>
          <span className="feature-row-arrow">→</span>
        </button>
        <button className="feature-row" onClick={() => setSwitchOpen(true)}>
          <span style={{ minWidth: 0 }}>
            <strong>Switch bot</strong>
            <span>Jump between Theo, Lusie, Pete, Edie and Susie without leaving the app.</span>
          </span>
          <span className="feature-row-arrow">→</span>
        </button>
      </section>

      <BotSwitcherSheet open={switchOpen} onClose={() => setSwitchOpen(false)} />
    </div>
  );
};
