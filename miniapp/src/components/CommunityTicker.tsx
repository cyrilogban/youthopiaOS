import React, { useEffect, useState } from 'react';
import { fetchCommunityStats, type CommunityStats } from '../services/api';

export const CommunityTicker: React.FC = () => {
  const [stats, setStats] = useState<CommunityStats>({
    totalMembers: 0,
    activeGroups: 0,
    quizzesPlayed: 0,
  });

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const data = await fetchCommunityStats();
      if (!cancelled) {
        setStats(data);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const items = [
    { icon: '👥', label: `${stats.totalMembers.toLocaleString()} Active Members` },
    { icon: '🏰', label: `${stats.activeGroups.toLocaleString()} Active Groups` },
    { icon: '🏆', label: `${stats.quizzesPlayed.toLocaleString()} Quizzes Played` },
    { icon: '✨', label: "Sharing God's Love All The Way" },
    { icon: '📖', label: 'YouThopia Bible Community' },
  ];

  return (
    <div
      style={{
        width: '100%',
        overflow: 'hidden',
        background: 'linear-gradient(90deg, rgba(245, 239, 255, 0.95) 0%, rgba(238, 230, 254, 0.95) 100%)',
        backdropFilter: 'blur(8px)',
        borderBottom: '1px solid rgba(216, 180, 254, 0.4)',
        padding: '6px 0',
        position: 'relative',
        userSelect: 'none',
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <style>{`
        @keyframes communityTickerLoop {
          0% {
            transform: translate3d(0, 0, 0);
          }
          100% {
            transform: translate3d(-50%, 0, 0);
          }
        }
        .community-ticker-track {
          display: flex;
          align-items: center;
          white-space: nowrap;
          width: max-content;
          animation: communityTickerLoop 28s linear infinite;
        }
        .community-ticker-track:hover,
        .community-ticker-track:active {
          animation-play-state: paused;
        }
      `}</style>

      <div className="community-ticker-track">
        {/* Track 1 */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 20, paddingRight: 20 }}>
          {items.map((item, idx) => (
            <span
              key={`track1-${idx}`}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                fontSize: 11,
                fontWeight: 700,
                color: '#581c87',
                letterSpacing: '0.01em',
              }}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
              <span style={{ color: '#c084fc', marginLeft: 12, opacity: 0.8 }}>•</span>
            </span>
          ))}
        </div>

        {/* Track 2 (Seamless Infinite Duplicate) */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 20, paddingRight: 20 }}>
          {items.map((item, idx) => (
            <span
              key={`track2-${idx}`}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                fontSize: 11,
                fontWeight: 700,
                color: '#581c87',
                letterSpacing: '0.01em',
              }}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
              <span style={{ color: '#c084fc', marginLeft: 12, opacity: 0.8 }}>•</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
