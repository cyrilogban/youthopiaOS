import React, { useEffect, useState } from 'react';
import { getRawInitData } from '../../services/telegram';
import { fetchSettings, fetchVotd, updateSettings, type VotdItem } from '../../services/api';
import { Card, Skeleton } from '../ui';

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: 20, fontWeight: 800, margin: '0 0 4px 0', color: 'var(--text-color)', letterSpacing: '-0.02em' }}>
          Scripture Hub
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
          Powered by Theo Bot &bull; Multi-Translation Scripture & Devotionals
        </p>
      </div>

      {/* Save Toast Notification */}
      {saveMessage && (
        <div
          style={{
            background: 'var(--success-bg)',
            border: '1px solid var(--success-border)',
            color: 'var(--success)',
            borderRadius: 'var(--radius-md)',
            padding: '10px 14px',
            fontSize: 12,
            fontWeight: 600,
            animation: 'fadeSlideIn 0.2s var(--ease) both',
          }}
        >
          {saveMessage}
        </div>
      )}

      {/* Dynamic VOTD Display Card */}
      <Card style={{ padding: 20 }} hover>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              color: 'var(--primary-purple)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            Daily Scripture Focus
          </span>
          <span
            style={{
              fontSize: 11,
              color: 'var(--primary-purple)',
              background: 'var(--purple-50)',
              border: '1px solid var(--purple-200)',
              padding: '2px 8px',
              borderRadius: 'var(--radius-full)',
              fontWeight: 600,
            }}
          >
            {selectedTranslation}
          </span>
        </div>

        {/* Translation Selector Tabs */}
        <div
          style={{
            display: 'flex',
            gap: 4,
            marginBottom: 18,
            background: 'var(--slate-100)',
            borderRadius: 'var(--radius-md)',
            padding: 4,
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
                  flex: 1,
                  background: active ? 'var(--surface)' : 'transparent',
                  color: active ? 'var(--primary-purple)' : 'var(--text-secondary)',
                  border: 'none',
                  borderRadius: 'calc(var(--radius-md) - 4px)',
                  padding: '8px 4px',
                  fontSize: 12,
                  fontWeight: 700,
                  cursor: 'pointer',
                  boxShadow: active ? 'var(--shadow-xs)' : 'none',
                  transition: 'all 0.15s var(--ease)',
                  opacity: isSaving ? 0.6 : 1,
                }}
              >
                {code}
              </button>
            );
          })}
        </div>

        {loadingVotd ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: '4px 0' }}>
            <Skeleton height={16} />
            <Skeleton height={16} width="92%" />
            <Skeleton height={16} width="70%" />
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: 12 }}>
              <div style={{ width: 4, alignSelf: 'stretch', borderRadius: 2, background: 'var(--grad-hero)', flexShrink: 0 }} />
              <p style={{ fontSize: 16, color: 'var(--text-color)', lineHeight: 1.75, fontStyle: 'italic', margin: 0 }}>
                &ldquo;{votd?.text}&rdquo;
              </p>
            </div>

            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderTop: '1px solid var(--slate-100)',
                paddingTop: 12,
                marginTop: 16,
              }}
            >
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{translationNames[selectedTranslation]}</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--primary-purple)' }}>{votd?.reference}</span>
            </div>
          </>
        )}
      </Card>
    </div>
  );
};
