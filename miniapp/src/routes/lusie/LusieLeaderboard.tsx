import React, { useEffect, useState } from 'react';
import { fetchLeaderboard, type LeaderboardItem } from '../../services/api';
import { Card, Pill, SectionTitle, Skeleton } from '../../components/ui';
import { RankBadge } from '../../components/RankBadge';

const MEDALS = ['🥇', '🥈', '🥉'];

export const LusieLeaderboard: React.FC = () => {
  const [members, setMembers] = useState<LeaderboardItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    void fetchLeaderboard().then((results) => {
      if (!cancelled) {
        setMembers(results);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="section-stack">
      <section className="page-heading">
        <h1>Top YouTopians.</h1>
        <p>Our most faithful players, ranked by the points they have earned across every challenge.</p>
      </section>

      <section className="section-group">
        <SectionTitle eyebrow="Community" right={<Pill color="slate">Top {members.length || 10}</Pill>}>Global leaderboard</SectionTitle>
        <Card style={{ padding: 10 }}>
          {loading ? (
            <div style={{ display: 'grid', gap: 8, padding: 6 }}>
              {[1, 2, 3, 4, 5].map((item) => <Skeleton key={item} height={48} />)}
            </div>
          ) : members.length ? (
            <div style={{ display: 'grid', gap: 3 }}>
              {members.map((item, index) => (
                <div
                  key={`${item.displayName}-${index}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '11px 8px',
                    borderBottom: index < members.length - 1 ? '1px solid var(--slate-100)' : undefined,
                  }}
                >
                  <strong style={{ width: 26, color: index < 3 ? 'var(--accent)' : 'var(--text-secondary)', fontSize: index < 3 ? 16 : 12 }}>
                    {MEDALS[index] ?? `#${index + 1}`}
                  </strong>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {item.displayName || 'Community member'}
                    </div>
                    {item.rankTitle && (
                      <div style={{ marginTop: 4 }}>
                        <RankBadge title={item.rankTitle} emoji={item.rankEmoji} color={item.rankBadgeColor} size="sm" />
                      </div>
                    )}
                  </div>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 700, whiteSpace: 'nowrap' }}>
                    {item.totalXp.toLocaleString()} XP
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted-copy" style={{ padding: 12 }}>The leaderboard will grow as members begin playing.</p>
          )}
        </Card>
      </section>

      <p className="muted-copy">Play a round with Lusie to earn points and claim your place here.</p>
    </div>
  );
};
