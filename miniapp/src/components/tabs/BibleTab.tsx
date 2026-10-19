import React, { useEffect, useState } from 'react';
import { getRawInitData } from '../../services/telegram';
import { fetchSettings, fetchVotd, updateSettings, type VotdItem } from '../../services/api';
import { Card, Pill, SectionTitle, Skeleton } from '../ui';

type TranslationCode = 'KJV' | 'ASV' | 'WEB' | 'BBE';
const TRANSLATIONS: TranslationCode[] = ['KJV', 'ASV', 'WEB', 'BBE'];

export const BibleTab: React.FC = () => {
  const [translation, setTranslation] = useState<TranslationCode>('KJV');
  const [votd, setVotd] = useState<VotdItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const settings = await fetchSettings(getRawInitData());
      const preferred = TRANSLATIONS.includes(settings.translation as TranslationCode) ? settings.translation as TranslationCode : 'KJV';
      const verse = await fetchVotd(preferred);
      if (!cancelled) {
        setTranslation(preferred);
        setVotd(verse);
        setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const selectTranslation = async (value: TranslationCode) => {
    setTranslation(value);
    setSaving(true);
    setLoading(true);
    const [nextVerse] = await Promise.all([
      fetchVotd(value),
      updateSettings(getRawInitData(), { translation: value, dailyDevotional: true }),
    ]);
    setVotd(nextVerse);
    setLoading(false);
    setSaving(false);
  };

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">Theo's space</span>
        <h1>Spend time in the Word.</h1>
        <p>Choose the translation that helps you read slowly, reflect clearly, and return often.</p>
      </section>

      <section>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 6, padding: 5, borderRadius: 'var(--radius-lg)', background: 'var(--surface-muted)' }}>
          {TRANSLATIONS.map((item) => {
            const selected = item === translation;
            return (
              <button
                key={item}
                disabled={saving}
                onClick={() => selectTranslation(item)}
                style={{ minHeight: 40, border: 0, borderRadius: 10, background: selected ? '#fff' : 'transparent', color: selected ? 'var(--primary-purple)' : 'var(--text-secondary)', boxShadow: selected ? 'var(--shadow-xs)' : 'none', fontSize: 12, fontWeight: 800, cursor: saving ? 'wait' : 'pointer' }}
              >
                {item}
              </button>
            );
          })}
        </div>
      </section>

      <Card style={{ padding: 20 }}>
        <SectionTitle eyebrow="Verse of the day" right={<Pill color="purple">{translation}</Pill>}>Read slowly</SectionTitle>
        {loading ? (
          <div style={{ display: 'grid', gap: 10 }}><Skeleton height={20} /><Skeleton height={20} width="92%" /><Skeleton height={20} width="74%" /><Skeleton height={12} width="36%" style={{ marginTop: 10 }} /></div>
        ) : (
          <article>
            <p style={{ margin: '2px 0 0', color: 'var(--ink)', fontFamily: 'Georgia, "Times New Roman", serif', fontSize: 22, lineHeight: 1.6 }}>
              “{votd?.text}”
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--slate-200)' }}>
              <strong style={{ color: 'var(--primary-purple)', fontSize: 14 }}>{votd?.reference}</strong>
              <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 700 }}>Daily Scripture</span>
            </div>
          </article>
        )}
      </Card>

      <section className="section-group">
        <SectionTitle eyebrow="Build next">Your Scripture library</SectionTitle>
        <Card style={{ padding: 16 }}>
          <div style={{ display: 'grid', gap: 12 }}>
            <div><strong style={{ fontSize: 14 }}>Saved verses</strong><p className="muted-copy" style={{ marginTop: 4 }}>Keep the verses you want to carry with you.</p></div>
            <div><strong style={{ fontSize: 14 }}>Reading plans</strong><p className="muted-copy" style={{ marginTop: 4 }}>A calm home for consistent Bible reading will live here.</p></div>
            <div><strong style={{ fontSize: 14 }}>Visual verse cards</strong><p className="muted-copy" style={{ marginTop: 4 }}>Shareable VOTD graphics are the next visual layer for Theo.</p></div>
          </div>
        </Card>
      </section>
    </div>
  );
};
