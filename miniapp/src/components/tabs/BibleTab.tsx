import React, { useEffect, useState } from 'react';
import { getRawInitData } from '../../services/telegram';
import { fetchSettings, updateSettings } from '../../services/api';

type TranslationCode = 'KJV' | 'ASV' | 'WEB' | 'BBE';

interface TranslationInfo {
  code: TranslationCode;
  name: string;
  text: string;
}

export const BibleTab: React.FC = () => {
  const [selectedTranslation, setSelectedTranslation] = useState<TranslationCode>('KJV');
  const [dailyDevotional, setDailyDevotional] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const translations: Record<TranslationCode, TranslationInfo> = {
    KJV: {
      code: 'KJV',
      name: 'King James Version',
      text: 'For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.',
    },
    ASV: {
      code: 'ASV',
      name: 'American Standard Version',
      text: 'For I know the thoughts that I think toward you, saith Jehovah, thoughts of peace, and not of evil, to give you hope in your latter end.',
    },
    WEB: {
      code: 'WEB',
      name: 'World English Bible',
      text: 'For I know the thoughts that I think toward you, says Yahweh, thoughts of peace, and not of evil, to give you hope and a future.',
    },
    BBE: {
      code: 'BBE',
      name: 'Bible in Basic English',
      text: 'For I have conscious knowledge of the thoughts which I have for you, says the Lord, thoughts of peace and not of evil, to give you a future and a hope.',
    },
  };

  useEffect(() => {
    let cancelled = false;
    const raw = getRawInitData();
    void (async () => {
      const settings = await fetchSettings(raw);
      if (cancelled) return;
      if (['KJV', 'ASV', 'WEB', 'BBE'].includes(settings.translation)) {
        setSelectedTranslation(settings.translation as TranslationCode);
      }
      setDailyDevotional(settings.dailyDevotional);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleTranslationChange = async (code: TranslationCode) => {
    setSelectedTranslation(code);
    setIsSaving(true);
    const raw = getRawInitData();
    const ok = await updateSettings(raw, { translation: code, dailyDevotional });
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

  const current = translations[selectedTranslation];

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

      {/* VOTD Display Card */}
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
            Daily Scripture Focus
          </span>
          <span style={{ fontSize: '11px', color: '#64748b', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
            {current.code}
          </span>
        </div>

        {/* Translation Selector Buttons (Synced Live to Supabase) */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
          {(Object.keys(translations) as TranslationCode[]).map((code) => (
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

        <p style={{ fontSize: '15px', color: '#1e293b', lineHeight: '1.7', fontStyle: 'italic', margin: '0 0 14px 0' }}>
          &ldquo;{current.text}&rdquo;
        </p>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #f1f5f9', paddingTop: '10px' }}>
          <span style={{ fontSize: '12px', color: '#64748b' }}>{current.name}</span>
          <span style={{ fontSize: '13px', fontWeight: 700, color: '#0f172a' }}>Jeremiah 29:11</span>
        </div>
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

      {/* Devotional Reflection Card */}
      <div
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '14px',
          padding: '18px',
        }}
      >
        <h3 style={{ fontSize: '14px', fontWeight: 700, margin: '0 0 8px 0', color: '#0f172a' }}>
          Daily Reflection
        </h3>
        <p style={{ fontSize: '13px', color: '#475569', lineHeight: '1.6', margin: 0 }}>
          God&apos;s promises provide unwavering assurance in seasons of transition. Trust His timeline as you build with purpose and faith.
        </p>
      </div>
    </div>
  );
};
