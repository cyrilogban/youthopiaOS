import React, { useEffect, useState } from 'react';
import { useAppData } from '../../context/AppData';
import { getRawInitData } from '../../services/telegram';
import { fetchSettings, updateSettings } from '../../services/api';
import { getSavedVerses } from '../../services/savedVerses';
import { Card, Pill, SectionTitle, SegmentedControl } from '../../components/ui';
import { RankBadge } from '../../components/RankBadge';

type TranslationCode = 'KJV' | 'ASV' | 'WEB' | 'BBE';
const TRANSLATIONS: TranslationCode[] = ['KJV', 'ASV', 'WEB', 'BBE'];

export const TheoProfile: React.FC = () => {
  const { user, verification, profile } = useAppData();
  const profileData = profile.status === 'ok' ? profile.profile : null;
  const isVerified = verification.status === 'verified';

  const [translation, setTranslation] = useState<TranslationCode>('KJV');
  const [dailyVerse, setDailyVerse] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedCount, setSavedCount] = useState(0);

  useEffect(() => {
    setSavedCount(getSavedVerses().length);
    let cancelled = false;
    void (async () => {
      const settings = await fetchSettings(getRawInitData());
      if (cancelled) return;
      if (TRANSLATIONS.includes(settings.translation as TranslationCode)) {
        setTranslation(settings.translation as TranslationCode);
      }
      setDailyVerse(settings.dailyDevotional);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const persist = async (nextTranslation: TranslationCode, nextDaily: boolean) => {
    setSaving(true);
    await updateSettings(getRawInitData(), { translation: nextTranslation, dailyDevotional: nextDaily });
    setSaving(false);
  };

  const onTranslation = (value: TranslationCode) => {
    setTranslation(value);
    void persist(value, dailyVerse);
  };

  const onToggleDaily = () => {
    const next = !dailyVerse;
    setDailyVerse(next);
    void persist(translation, next);
  };

  const displayName = user?.firstName || profileData?.displayName || 'Member';
  const initial = displayName[0]?.toUpperCase() || 'Y';
  const totalXp = profileData?.totalXp ?? 0;
  const computedLevel = Math.max(1, Math.floor(totalXp / 100) + 1);
  const level = profileData?.level && profileData.level > 1 ? profileData.level : computedLevel;

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">Your YouTopian identity</span>
        <h1>{displayName}</h1>
        {user?.username && <p>@{user.username}</p>}
      </section>

      <Card style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span className="profile-avatar" style={{ width: 58, height: 58, fontSize: 20 }}>
            {user?.photoUrl ? <img src={user.photoUrl} alt={displayName} /> : initial}
          </span>
          <div style={{ display: 'grid', gap: 8 }}>
            {profileData?.rankTitle && (
              <RankBadge title={profileData.rankTitle} emoji={profileData.rankEmoji} color={profileData.rankBadgeColor} size="md" />
            )}
            <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
              <Pill color={isVerified ? 'success' : 'warning'}>{isVerified ? 'Verified member' : 'Identity pending'}</Pill>
              <Pill color="purple">Trust {profileData?.trustScore ?? 100}</Pill>
            </div>
          </div>
        </div>

        <div className="metric-grid" style={{ marginTop: 20 }}>
          <div className="metric-tile">
            <div className="metric-label">Level</div>
            <div className="metric-value">{level}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-label">XP</div>
            <div className="metric-value">{totalXp.toLocaleString()}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-label">Saved</div>
            <div className="metric-value">{savedCount}</div>
          </div>
        </div>
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Your reading" right={<Pill color="purple">{translation}</Pill>}>
          Scripture preferences
        </SectionTitle>
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'grid', gap: 14 }}>
            <div>
              <strong style={{ fontSize: 13 }}>Preferred translation</strong>
              <div style={{ marginTop: 10 }}>
                <SegmentedControl options={TRANSLATIONS} value={translation} onChange={onTranslation} disabled={saving} />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
              <div>
                <strong style={{ fontSize: 13 }}>Daily verse</strong>
                <p className="muted-copy" style={{ marginTop: 3 }}>
                  Receive Verse of the Day from Theo.
                </p>
              </div>
              <button
                onClick={onToggleDaily}
                style={{
                  minWidth: 68,
                  minHeight: 40,
                  border: '1px solid var(--purple-200)',
                  borderRadius: 'var(--radius-full)',
                  background: dailyVerse ? 'var(--accent)' : 'var(--surface)',
                  color: dailyVerse ? '#fff' : 'var(--text-secondary)',
                  fontSize: 12,
                  fontWeight: 800,
                  cursor: 'pointer',
                }}
              >
                {dailyVerse ? 'On' : 'Off'}
              </button>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
              <div>
                <strong style={{ fontSize: 13 }}>Reading streak</strong>
                <p className="muted-copy" style={{ marginTop: 3 }}>
                  Consistent reading streaks are coming soon.
                </p>
              </div>
              <Pill color="slate">Soon</Pill>
            </div>
          </div>
        </Card>
      </section>

      <a
        className="secondary-button"
        href="https://t.me/theobiblebot"
        target="_blank"
        rel="noreferrer"
        style={{ width: '100%' }}
      >
        Open Theo in Telegram
      </a>
    </div>
  );
};
