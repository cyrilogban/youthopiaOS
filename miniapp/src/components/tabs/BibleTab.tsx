import React, { useEffect, useState } from 'react';
import { getRawInitData } from '../../services/telegram';
import { fetchSettings, fetchVotd, updateSettings, type VotdItem } from '../../services/api';
import { Card, Pill, SectionTitle, Skeleton } from '../ui';

type TranslationCode = 'KJV' | 'ASV' | 'WEB' | 'BBE';

const TRANSLATIONS: TranslationCode[] = ['KJV', 'ASV', 'WEB', 'BBE'];

export const BibleTab: React.FC = () => {
  const [selectedTranslation, setSelectedTranslation] = useState<TranslationCode>('KJV');
  const [votd, setVotd] = useState<VotdItem | null>(null);
  const [loadingVotd, setLoadingVotd] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const translationNames: Record<TranslationCode, string> = {
    KJV: 'King James Version',
    ASV: 'American Standard Version',
    WEB: 'World English Bible',
    BBE: 'Bible in Basic English',
  };

  useEffect(() => {
    let cancelled = false;
    const raw = getRawInitData();
    void (async () => {
      const settings = await fetchSettings(raw);
      if (cancelled) return;
      const initialTrans = TRANSLATIONS.includes(settings.translation as TranslationCode)
        ? (settings.translation as TranslationCode)
        : 'KJV';
      setSelectedTranslation(initialTrans);

      const item = await fetchVotd(initialTrans);
      if (!cancelled) {
        setVotd(item);
        setLoadingVotd(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleTranslationChange = async (code: TranslationCode) => {
    setSelectedTranslation(code);
    setIsSaving(true);
    setLoadingVotd(true);
    const raw = getRawInitData();

    const [ok, newVotd] = await Promise.all([
      updateSettings(raw, { translation: code, dailyDevotional: true }),
      fetchVotd(code),
    ]);

    setVotd(newVotd);
    setLoadingVotd(false);
    setIsSaving(false);

    if (ok) {
      setSaveMessage(`Translation saved: ${code}`);
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  return (
    <div className="section-stack">
      <section
        style={{
          borderRadius: 28,
          padding: 20,
          color: '#fff',
          background: 'var(--grad-bible)',
          boxShadow: 'var(--shadow-purple)',
        }}
      >
        <Pill color="deep" style={{ background: 'rgba(255,255,255,0.16)', borderColor: 'rgba(255,255,255,0.26)', marginBottom: 12 }}>
          Theo Scripture Hub
        </Pill>
        <h2 style={{ margin: 0, fontSize: 26, lineHeight: 1.08, fontWeight: 950 }}>Daily Scripture, beautifully centered.</h2>
        <p style={{ margin: '9px 0 0', color: 'rgba(255,255,255,0.8)', fontSize: 13, lineHeight: 1.55 }}>
          Read the Verse of the Day, switch translations, and prepare the foundation for visual Scripture cards.
        </p>
      </section>

      {saveMessage && (
        <div
          style={{
            background: 'var(--success-bg)',
            border: '1px solid var(--success-border)',
            color: 'var(--success)',
            borderRadius: 'var(--radius-lg)',
            padding: '11px 14px',
            fontSize: 12,
            fontWeight: 800,
          }}
        >
          {saveMessage}
        </div>
      )}

      <Card style={{ padding: 18 }} hover>
        <SectionTitle eyebrow="Verse of the Day" right={<Pill color="purple">{selectedTranslation}</Pill>}>
          Scripture Card
        </SectionTitle>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
            gap: 6,
            marginBottom: 16,
            padding: 5,
            borderRadius: 'var(--radius-lg)',
            background: 'var(--surface-muted)',
          }}
        >
          {TRANSLATIONS.map((code) => {
            const active = selectedTranslation === code;
            return (
              <button
                key={code}
                disabled={isSaving}
                onClick={() => handleTranslationChange(code)}
                style={{
                  minHeight: 38,
                  border: 0,
                  borderRadius: 'var(--radius-md)',
                  background: active ? '#fff' : 'transparent',
                  color: active ? 'var(--primary-purple)' : 'var(--text-secondary)',
                  boxShadow: active ? 'var(--shadow-xs)' : 'none',
                  fontSize: 12,
                  fontWeight: 900,
                  cursor: 'pointer',
                  opacity: isSaving ? 0.62 : 1,
                }}
              >
                {code}
              </button>
            );
          })}
        </div>

        {loadingVotd ? (
          <div style={{ display: 'grid', gap: 9 }}>
            <Skeleton height={17} />
            <Skeleton height={17} width="92%" />
            <Skeleton height={17} width="74%" />
            <Skeleton height={12} width="45%" style={{ marginTop: 8 }} />
          </div>
        ) : (
          <div
            style={{
              padding: 18,
              borderRadius: 22,
              background: 'linear-gradient(160deg,#ffffff,#f7f2ff)',
              border: '1px solid var(--purple-100)',
            }}
          >
            <div className="eyebrow" style={{ marginBottom: 14 }}>{translationNames[selectedTranslation]}</div>
            <p style={{ margin: 0, color: 'var(--text-color)', fontSize: 18, lineHeight: 1.78, fontWeight: 600 }}>
              "{votd?.text}"
            </p>
            <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
              <strong style={{ color: 'var(--primary-purple)', fontSize: 14 }}>{votd?.reference}</strong>
              <Pill color="slate">Visual card ready soon</Pill>
            </div>
          </div>
        )}
      </Card>

      <Card style={{ padding: 18 }}>
        <SectionTitle eyebrow="Next Layer">Theo Visual Features</SectionTitle>
        <div style={{ display: 'grid', gap: 10 }}>
          {['Shareable VOTD graphics', 'Saved verse gallery', 'AOTD companion card', 'Reading-plan progress'].map((item) => (
            <div key={item} style={{ padding: 12, borderRadius: 'var(--radius-lg)', background: '#fff', border: '1px solid var(--purple-100)', fontSize: 13, fontWeight: 750 }}>
              {item}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
