import React, { useEffect, useState } from 'react';
import { getRawInitData } from '../../services/telegram';
import { fetchSettings, fetchVotd, type VotdItem } from '../../services/api';
import { FeedPost, type FeedPostData } from '../../components/feed/FeedPost';
import { Skeleton } from '../../components/ui';

const SAMPLE_POSTS: FeedPostData[] = [
  {
    id: 'sample-aotd',
    type: 'Affirmation',
    sourceName: 'Theo',
    sourceHandle: '@theobiblebot',
    timeLabel: 'Today',
    body: 'I am rooted in grace, I walk in purpose, and I carry peace into everything I touch today.',
    reference: 'Affirmation of the Day',
    sample: true,
  },
  {
    id: 'sample-prayer',
    type: 'Prayer',
    sourceName: 'Theo',
    sourceHandle: '@theobiblebot',
    timeLabel: 'Today',
    body: 'Father, thank You for this day. Steady my heart, order my steps, and let my words bring life to everyone I meet. Amen.',
    reference: 'Prayer of the Day',
    sample: true,
  },
  {
    id: 'sample-card',
    type: 'Card',
    sourceName: 'Theo',
    sourceHandle: '@theobiblebot',
    timeLabel: 'Today',
    body: 'Your word is a lamp to my feet, and a light to my path. - Psalm 119:105',
    reference: 'Psalm 119:105',
    visual: { eyebrow: 'Verse card', text: '“Your word is a lamp to my feet, and a light to my path.”' },
    sample: true,
  },
];

export const TheoHome: React.FC = () => {
  const [votd, setVotd] = useState<VotdItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const settings = await fetchSettings(getRawInitData());
      const verse = await fetchVotd(settings.translation);
      if (!cancelled) {
        setVotd(verse);
        setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const votdPost: FeedPostData | null = votd
    ? {
        id: `votd-${votd.reference}-${votd.translation}`,
        type: 'Verse',
        sourceName: 'Theo',
        sourceHandle: '@theobiblebot',
        timeLabel: 'Today',
        body: `“${votd.text}”`,
        reference: `${votd.reference} · ${votd.translation}`,
        translation: votd.translation,
        verseStyle: true,
      }
    : null;

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Your daily moments.</h1>
        <p>Scripture, affirmations, and prayers, gathered in one place. Save or share anything that speaks to you.</p>
      </section>

      {loading ? (
        <div className="feed">
          <div className="post" style={{ padding: 16 }}>
            <Skeleton height={14} width="40%" />
            <Skeleton height={22} style={{ marginTop: 16 }} />
            <Skeleton height={22} width="86%" style={{ marginTop: 9 }} />
            <Skeleton height={22} width="64%" style={{ marginTop: 9 }} />
          </div>
        </div>
      ) : (
        <div className="feed">
          {votdPost && <FeedPost post={votdPost} />}
          {SAMPLE_POSTS.map((post) => (
            <FeedPost key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
};
