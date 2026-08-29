import React, { useEffect, useState } from 'react';
import { getRawInitData } from '../../services/telegram';
import { fetchSettings, fetchVotd, updateSettings, type VotdItem } from '../../services/api';

type TranslationCode = 'KJV' | 'ASV' | 'WEB' | 'BBE';

export const BibleTab: React.FC = () => {
  const [selectedTranslation, setSelectedTranslation] = useState<TranslationCode>('KJV');
  const [dailyDevotional, setDailyDevotional] = useState<boolean>(true);
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
      const initialTrans = ['KJV', 'ASV', 'WEB', 'BBE'].includes(settings.translation)
        ? (settings.translation as TranslationCode)
        : 'KJV';
      setSelectedTranslation(initialTrans);
      setDailyDevotional(settings.dailyDevotional);

      // Fetch dynamic VOTD from Supabase + Bible API for the user's translation
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

    // Parallel fetch: save preference to Supabase AND load dynamic verse text for new translation
    const [ok, newVotd] = await Promise.all([
      updateSettings(raw, { translation: code, dailyDevotional }),
      fetchVotd(code),
    ]);

    setVotd(newVotd);
    setLoadingVotd(false);
    setIsSaving(false);

    if (ok) {
      setSaveMessage(`Translation saved to Supabase: ${code}`);
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  const handleToggleDevotional = async () => {
    const nextVal = !dailyDevotional;
    setDailyDevotional(nextVal);
    setIsSaving(true);
    const raw = getRawInitData();
    const ok = await updateSettings(raw, { translation: selectedTranslation, dailyDevotional: nextVal });
    setIsSaving(false);
    if (ok) {
      setSaveMessage(`Daily verse reminder ${nextVal ? 'enabled' : 'disabled'} in Supabase`);
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 4px 0', color: '#0f172a' }}>
          Scripture Hub
        </h2>
        <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
          Powered by Theo Bot &bull; Multi-Translation Scripture & Devotionals
        </p>
      </div>

      {/* Save Toast Notification */}
      {saveMessage && (
        <div
          style={{
            backgroundColor: '#f0fdf4',
            border: '1px solid #bbf7d0',
            color: '#15803d',
            borderRadius: '10px',
            padding: '10px 14px',
            fontSize: '12px',
            fontWeight: 600,
          }}
        >
          {saveMessage}
        </div>
      )}

      {/* Dynamic VOTD Display Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '14px',
          padding: '20px',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <span style={{ fontSize: '12px', fontWeight: 700, color: '#6d28d9', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Daily Scripture Focus (Supabase Live)
          </span>
          <span style={{ fontSize: '11px', color: '#64748b', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
            {selectedTranslation}
          </span>
        </div>

        {/* Translation Selector Buttons (Synced Live to Supabase) */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
          {(['KJV', 'ASV', 'WEB', 'BBE'] as TranslationCode[]).map((code) => (
            <button
              key={code}
              disabled={isSaving}
              onClick={() => handleTranslationChange(code)}
              style={{
                background: selectedTranslation === code ? '#6d28d9' : '#f1f5f9',
                color: selectedTranslation === code ? '#ffffff' : '#64748b',
                border: 'none',
                borderRadius: '6px',
                padding: '5px 12px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                opacity: isSaving ? 0.7 : 1,
              }}
            >
              {code}
            </button>
          ))}
        </div>

        {loadingVotd ? (
          <div style={{ fontSize: '13px', color: '#64748b', margin: '12px 0' }}>
            Fetching today&apos;s active Scripture from Supabase…
          </div>
        ) : (
          <>
            <p style={{ fontSize: '15px', color: '#1e293b', lineHeight: '1.7', fontStyle: 'italic', margin: '0 0 14px 0' }}>
              &ldquo;{votd?.text}&rdquo;
            </p>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #f1f5f9', paddingTop: '10px' }}>
              <span style={{ fontSize: '12px', color: '#64748b' }}>{translationNames[selectedTranslation]}</span>
              <span style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>{votd?.reference}</span>
            </div>
          </>
        )}
      </div>

      {/* Supabase Preference Settings Card */}
      <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '14px', padding: '18px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#0f172a' }}>Daily Verse Reminders</div>
            <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>Receive Theo&apos;s 6:00 AM daily devotional in Telegram</div>
          </div>
          <button
            disabled={isSaving}
            onClick={handleToggleDevotional}
            style={{
              backgroundColor: dailyDevotional ? '#16a34a' : '#cbd5e1',
              color: '#ffffff',
              border: 'none',
              borderRadius: '20px',
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {dailyDevotional ? 'Enabled' : 'Disabled'}
          </button>
        </div>
      </div>
    </div>
  );
};
