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
    { label: `${stats.totalMembers.toLocaleString()} Active Members` },
    { label: `${stats.activeGroups.toLocaleString()} Active Groups` },
    { label: `${stats.quizzesPlayed.toLocaleString()} Quizzes Played` },
    { label: "Sharing God's Love All The Way" },
    { label: 'YouThopia Bible Community' },
  ];

  return (
    <div
      style={{
        width: '100%',
        overflow: 'hidden',
        background: 'linear-gradient(90deg, rgba(250, 248, 255, 0.92) 0%, rgba(243, 238, 255, 0.92) 100%)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(221, 214, 254, 0.5)',
        padding: '7px 0',
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
          animation: communityTickerLoop 32s linear infinite;
        }
        .community-ticker-track:hover,
        .community-ticker-track:active {
          animation-play-state: paused;
        }
        .ticker-capsule {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          padding: 4px 12px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.85);
          border: 1px solid rgba(221, 214, 254, 0.75);
          box-shadow: 0 1px 3px rgba(109, 40, 217, 0.06);
          font-size: 11px;
          font-weight: 750;
          color: var(--primary-purple);
          letter-spacing: 0.01em;
          transition: transform 0.15s ease, background 0.15s ease;
        }
        .ticker-capsule:hover {
          background: #ffffff;
          transform: translateY(-1px);
        }
        .ticker-dot {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: var(--primary-purple);
          opacity: 0.75;
          flex-shrink: 0;
        }
      `}</style>

      <div className="community-ticker-track">
        {/* Track 1 */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, paddingRight: 12 }}>
          {items.map((item, idx) => (
            <span key={`track1-${idx}`} className="ticker-capsule">
              <span className="ticker-dot" />
              <span>{item.label}</span>
            </span>
          ))}
        </div>

        {/* Track 2 (Seamless Infinite Duplicate) */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, paddingRight: 12 }}>
          {items.map((item, idx) => (
            <span key={`track2-${idx}`} className="ticker-capsule">
              <span className="ticker-dot" />
              <span>{item.label}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
