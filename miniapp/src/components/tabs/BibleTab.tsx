import React, { useEffect, useState } from 'react';
import { VerseOfTheDay } from '@youversion/platform-react-ui';
import { getRawInitData } from '../../services/telegram';
import {
  fetchSettings,
  fetchVotd,
  updateSettings,
  fetchFeaturedVerses,
  fetchSavedVerses,
  fetchLikedVerses,
  type VotdItem,
  type FeaturedVerse,
  type SavedVerseRow,
} from '../../services/api';
import { VerseCard } from '../bible/VerseCard';
import { EmptyState, Skeleton } from '../ui';

type SubTabId = 'featured' | 'discover' | 'saved';

type TranslationCode = 'KJV' | 'ASV' | 'WEB' | 'BBE';
const TRANSLATIONS: TranslationCode[] = ['KJV', 'ASV', 'WEB', 'BBE'];

// Discovery feed curated pool of life-changing verses for infinite scroll
const DISCOVERY_VERSES = [
  { reference: 'JHN.3.16', text: 'For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.' },
  { reference: 'PHP.4.13', text: 'I can do all things through Christ which strengtheneth me.' },
  { reference: 'JER.29.11', text: 'For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.' },
  { reference: 'ROM.8.28', text: 'And we know that all things work together for good to them that love God, to them who are the called according to his purpose.' },
  { reference: 'PSA.23.1', text: 'The LORD is my shepherd; I shall not want.' },
  { reference: 'PRO.3.5-6', text: 'Trust in the LORD with all thine heart; and lean not unto thine own understanding. In all thy ways acknowledge him, and he shall direct thy paths.' },
  { reference: 'ISA.40.31', text: 'But they that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary; and they shall walk, and not faint.' },
  { reference: 'MAT.6.33', text: 'But seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you.' },
  { reference: '2TI.1.7', text: 'For God hath not given us the spirit of fear; but of power, and of love, and of a sound mind.' },
  { reference: 'JHN.14.27', text: 'Peace I leave with you, my peace I give unto you: not as the world giveth, give I unto you. Let not your heart be troubled, neither let it be afraid.' },
  { reference: 'GAL.5.22-23', text: 'But the fruit of the Spirit is love, joy, peace, longsuffering, gentleness, goodness, faith, meekness, temperance: against such there is no law.' },
  { reference: 'ROM.12.2', text: 'And be not conformed to this world: but be ye transformed by the renewing of your mind, that ye may prove what is that good, and acceptable, and perfect, will of God.' },
];

export const BibleTab: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<SubTabId>('featured');
  const [translation, setTranslation] = useState<TranslationCode>('KJV');
  const [votd, setVotd] = useState<VotdItem | null>(null);
  const [featuredVerses, setFeaturedVerses] = useState<FeaturedVerse[]>([]);
  const [savedVerses, setSavedVerses] = useState<SavedVerseRow[]>([]);
  const [likedRefs, setLikedRefs] = useState<Set<string>>(new Set());
  const [savedRefs, setSavedRefs] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [savingTranslation, setSavingTranslation] = useState(false);

  // Discover feed cursor pagination
  const [discoverBatchCount, setDiscoverBatchCount] = useState(4);

  const rawInitData = getRawInitData();

  useEffect(() => {
    let cancelled = false;

    void (async () => {
      setLoading(true);
      try {
        const [settings, initialVotd, featured, saved, likes] = await Promise.all([
          fetchSettings(rawInitData),
          fetchVotd('KJV'),
          fetchFeaturedVerses(),
          fetchSavedVerses(rawInitData),
          fetchLikedVerses(rawInitData),
        ]);

        if (!cancelled) {
          const preferred = TRANSLATIONS.includes(settings.translation as TranslationCode)
            ? (settings.translation as TranslationCode)
            : 'KJV';

          setTranslation(preferred);
          setVotd(initialVotd);
          setFeaturedVerses(featured);
          setSavedVerses(saved);
          setLikedRefs(new Set(likes));
          setSavedRefs(new Set(saved.map((s) => s.verse_reference)));
        }
      } catch (err) {
        console.warn('Error loading Bible tab data:', err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [rawInitData]);

  const selectTranslation = async (value: TranslationCode) => {
    setTranslation(value);
    setSavingTranslation(true);
    try {
      const [nextVerse] = await Promise.all([
        fetchVotd(value),
        updateSettings(rawInitData, { translation: value, dailyDevotional: true }),
      ]);
      setVotd(nextVerse);
    } finally {
      setSavingTranslation(false);
    }
  };

  const handleSavedListReload = async () => {
    const list = await fetchSavedVerses(rawInitData);
    setSavedVerses(list);
    setSavedRefs(new Set(list.map((s) => s.verse_reference)));
  };

  return (
    <div className="section-stack" style={{ gap: 20 }}>
      {/* Header */}
      <section className="page-heading">
        <span className="quiet-chip">Theo's space</span>
        <h1 style={{ fontSize: 26, fontWeight: 800 }}>Spend time in the Word.</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Social Scripture feed, daily encouragement, and your personal Bible library.
        </p>
      </section>

      {/* Sub-Tab Navigation: [ Featured ] [ Discover ] [ Saved ] */}
      <section>
        <div
          role="tablist"
          aria-label="Bible feed sub tabs"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
            gap: 6,
            padding: 4,
            borderRadius: '12px',
            background: '#F3F4F6',
            border: '1px solid #E5E7EB',
          }}
        >
          {(
            [
              { id: 'featured', label: 'Featured' },
              { id: 'discover', label: 'Discover' },
              { id: 'saved', label: `Saved${savedVerses.length > 0 ? ` (${savedVerses.length})` : ''}` },
            ] as const
          ).map((tab) => {
            const active = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                role="tab"
                aria-selected={active}
                onClick={() => setActiveSubTab(tab.id)}
                style={{
                  minHeight: 38,
                  border: 0,
                  borderRadius: 8,
                  background: active ? '#000000' : 'transparent',
                  color: active ? '#FFFFFF' : '#4B5563',
                  boxShadow: active ? '0 2px 6px rgba(0, 0, 0, 0.12)' : 'none',
                  fontSize: 13,
                  fontWeight: active ? 700 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  fontFamily: "'Poppins', sans-serif",
                }}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </section>

      {/* ------------------------------------------------------------- */}
      {/* SUB-TAB 1: FEATURED (Admin Curated Verses + VOTD)             */}
      {/* ------------------------------------------------------------- */}
      {activeSubTab === 'featured' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Translation Selector */}
          <section>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#6B7280', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Translation
            </div>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
                gap: 6,
                padding: 4,
                borderRadius: '10px',
                background: '#F3F4F6',
                border: '1px solid #E5E7EB',
              }}
            >
              {TRANSLATIONS.map((item) => {
                const selected = item === translation;
                return (
                  <button
                    key={item}
                    disabled={savingTranslation}
                    onClick={() => selectTranslation(item)}
                    style={{
                      minHeight: 34,
                      border: 0,
                      borderRadius: 6,
                      background: selected ? '#000000' : 'transparent',
                      color: selected ? '#FFFFFF' : '#4B5563',
                      boxShadow: selected ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                      fontSize: 12,
                      fontWeight: selected ? 700 : 500,
                      cursor: savingTranslation ? 'wait' : 'pointer',
                    }}
                  >
                    {item}
                  </button>
                );
              })}
            </div>
          </section>

          {/* Today's Pick / Verse of the Day Card */}
          {loading ? (
            <div style={{ display: 'grid', gap: 12 }}>
              <Skeleton height={200} style={{ borderRadius: 16 }} />
            </div>
          ) : votd ? (
            <VerseCard
              reference={votd.reference}
              text={votd.text}
              translation={translation}
              label="Today's Pick"
              initialLiked={likedRefs.has(votd.reference)}
              initialSaved={savedRefs.has(votd.reference)}
              onBookmarkChange={() => void handleSavedListReload()}
            />
          ) : null}

          {/* Curated Feed Section */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: 16, fontWeight: 800, color: '#111827', margin: 0 }}>
                Community Highlights
              </h2>
              <span style={{ fontSize: 11, fontWeight: 700, color: '#000000', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Featured
              </span>
            </div>

            {featuredVerses.map((fv) => (
              <VerseCard
                key={fv.id || fv.verse_reference}
                reference={fv.verse_reference}
                text={fv.verse_text}
                translation={fv.translation || 'KJV'}
                label="Featured"
                initialLiked={likedRefs.has(fv.verse_reference)}
                initialSaved={savedRefs.has(fv.verse_reference)}
                onBookmarkChange={() => void handleSavedListReload()}
              />
            ))}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* SUB-TAB 2: DISCOVER (YouVersion Verse of the Day + Feed)      */}
      {/* ------------------------------------------------------------- */}
      {activeSubTab === 'discover' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* YouVersion Verse of the Day Component (Clean Minimalist Card) */}
          <section
            style={{
              padding: '16px',
              borderRadius: '16px',
              background: '#FFFFFF',
              border: '1px solid #E5E7EB',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.04)',
              overflow: 'hidden',
            }}
          >
            <VerseOfTheDay
              background="light"
              showSunIcon={true}
              showShareButton={true}
              showBibleAppAttribution={false}
            />
          </section>

          {/* Infinite Scroll Discovery Stream */}
          <section style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: 16, fontWeight: 800, color: '#111827', margin: 0 }}>
                Explore Scripture
              </h2>
              <span style={{ fontSize: 11, color: '#6B7280', fontWeight: 500 }}>
                Showing {Math.min(discoverBatchCount, DISCOVERY_VERSES.length)} of {DISCOVERY_VERSES.length}
              </span>
            </div>

            {DISCOVERY_VERSES.slice(0, discoverBatchCount).map((v) => (
              <VerseCard
                key={v.reference}
                reference={v.reference}
                text={v.text}
                translation="KJV"
                label="Discover"
                initialLiked={likedRefs.has(v.reference)}
                initialSaved={savedRefs.has(v.reference)}
                onBookmarkChange={() => void handleSavedListReload()}
              />
            ))}

            {/* Cursor pagination: Load More Button */}
            {discoverBatchCount < DISCOVERY_VERSES.length && (
              <button
                type="button"
                onClick={() => setDiscoverBatchCount((prev) => Math.min(prev + 4, DISCOVERY_VERSES.length))}
                style={{
                  padding: '13px 20px',
                  borderRadius: '12px',
                  border: '1px solid #000000',
                  background: '#000000',
                  color: '#FFFFFF',
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: 'pointer',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
                  transition: 'all 0.15s ease',
                  fontFamily: "'Poppins', sans-serif",
                }}
              >
                Scroll for more verses ↓
              </button>
            )}
          </section>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* SUB-TAB 3: SAVED (User's Bookmarked Collection from Supabase) */}
      {/* ------------------------------------------------------------- */}
      {activeSubTab === 'saved' && (
        <div>
          {savedVerses.length === 0 ? (
            <div style={{ padding: '30px 10px' }}>
              <EmptyState
                title="No saved verses yet."
                body="Bookmark a verse from the feed to see it here."
                action={
                  <button
                    className="primary-button"
                    onClick={() => setActiveSubTab('featured')}
                    style={{
                      background: '#000000',
                      color: '#FFFFFF',
                      border: 0,
                      padding: '12px 24px',
                      borderRadius: 10,
                      fontWeight: 700,
                      fontSize: 13,
                      cursor: 'pointer',
                    }}
                  >
                    Browse Feed
                  </button>
                }
              />
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: 16, fontWeight: 800, color: '#111827', margin: 0 }}>
                  Your Saved Collection
                </h2>
                <span style={{ fontSize: 12, fontWeight: 700, color: '#111827' }}>
                  {savedVerses.length} {savedVerses.length === 1 ? 'verse' : 'verses'}
                </span>
              </div>

              {savedVerses.map((sv) => (
                <VerseCard
                  key={sv.id || sv.verse_reference}
                  reference={sv.verse_reference}
                  text={sv.verse_text}
                  translation={sv.translation || 'KJV'}
                  label="Saved"
                  initialLiked={likedRefs.has(sv.verse_reference)}
                  initialSaved={true}
                  onBookmarkChange={() => void handleSavedListReload()}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
