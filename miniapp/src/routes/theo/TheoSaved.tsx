import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRawInitData } from '../../services/telegram';
import { fetchSavedVerses, fetchLikedVerses, type SavedVerseRow } from '../../services/api';
import { VerseCard } from '../../components/bible/VerseCard';
import { EmptyState, Skeleton } from '../../components/ui';

export const TheoSaved: React.FC = () => {
  const navigate = useNavigate();
  const [verses, setVerses] = useState<SavedVerseRow[]>([]);
  const [likedRefs, setLikedRefs] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  const rawInitData = getRawInitData();

  const reload = async () => {
    try {
      const [saved, likes] = await Promise.all([
        fetchSavedVerses(rawInitData),
        fetchLikedVerses(rawInitData),
      ]);
      setVerses(saved);
      setLikedRefs(new Set(likes));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void reload();
  }, [rawInitData]);

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">Your Scripture library</span>
        <h1 style={{ fontSize: 26, fontWeight: 800 }}>Saved verses.</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          The verses you keep close. Bookmark a verse from the feed to see it here.
        </p>
      </section>

      {loading ? (
        <div style={{ display: 'grid', gap: 12 }}>
          <Skeleton height={180} style={{ borderRadius: 20 }} />
          <Skeleton height={180} style={{ borderRadius: 20 }} />
        </div>
      ) : verses.length === 0 ? (
        <EmptyState
          title="No saved verses yet."
          body="Bookmark a verse from the feed to see it here."
          action={
            <button
              className="primary-button"
              onClick={() => navigate('/theo/bible')}
              style={{
                background: 'linear-gradient(135deg, #4D148C 0%, #3A1078 100%)',
                color: '#FFFFFF',
                border: 0,
                padding: '12px 24px',
                borderRadius: 12,
                fontWeight: 700,
                fontSize: 13,
                cursor: 'pointer',
              }}
            >
              Explore Bible Feed
            </button>
          }
        />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {verses.map((verse) => (
            <VerseCard
              key={verse.id || verse.verse_reference}
              reference={verse.verse_reference}
              text={verse.verse_text}
              translation={verse.translation || 'KJV'}
              label="Saved"
              initialLiked={likedRefs.has(verse.verse_reference)}
              initialSaved={true}
              onBookmarkChange={() => void reload()}
            />
          ))}
        </div>
      )}
    </div>
  );
};
