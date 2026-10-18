/**
 * TourOverlay — the in-app guided YouThopia Tour (the same 5 pages all 5 bots
 * serve). Full-screen bottom-sheet: swipe-through pages, then Finish to be
 * marked oriented and claim the one-time +50 YP welcome boost.
 */
import React, { useState } from 'react';
import { Pill } from './ui';
import { completeCommunityTour, type Tour, type TourCompleteResult } from '../services/api';

const TOUR_SEEN_KEY = 'youthopia_tour_seen_v1';

export function markTourAsSeen(): void {
  try {
    window.localStorage.setItem(TOUR_SEEN_KEY, '1');
  } catch {
    /* storage unavailable — the tour simply opens again next time */
  }
}

interface TourOverlayProps {
  tour: Tour | null;
  /** True when the caller is verified and has never completed orientation. */
  canEarnXp: boolean;
  rawInitData: string | null;
  onClose: () => void;
  /** Fired after the Finish call completes so the shell can refresh XP/rank. */
  onFinish: (result: TourCompleteResult) => void;
}

const renderPage = (page: NonNullable<Tour['pages'][number]>) => (
  <>
    {page.blocks?.map((block) => (
      <div key={block.label} style={{ display: 'grid', gap: 4 }}>
        <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--primary-purple)' }}>
          {block.label}
        </div>
        <p className="muted-copy" style={{ fontSize: 13.5 }}>{block.text}</p>
      </div>
    ))}

    {page.bullets && (
      <div style={{ display: 'grid', gap: 10 }}>
        {page.bullets.map((bullet) => (
          <div key={bullet} style={{ display: 'flex', gap: 9, alignItems: 'flex-start' }}>
            <span style={{ color: 'var(--primary-purple)', fontSize: 12, lineHeight: 1.6 }}>✿</span>
            <p className="muted-copy" style={{ flex: 1, fontSize: 13 }}>&nbsp;{bullet}</p>
          </div>
        ))}
      </div>
    )}

    {page.bots && (
      <div style={{ display: 'grid', gap: 9 }}>
        {page.bots.map((bot) => (
          <div
            key={bot.handle}
            style={{
              display: 'grid',
              gap: 2,
              padding: '10px 12px',
              border: '1px solid var(--slate-200)',
              borderRadius: 'var(--radius-md)',
              background: 'var(--surface-soft)',
            }}
          >
            <div style={{ fontSize: 13.5, fontWeight: 750 }}>
              {bot.name} <span style={{ color: 'var(--text-muted)', fontWeight: 650 }}>({bot.short})</span>
              <span style={{ marginLeft: 6, color: 'var(--primary-purple)', fontSize: 12, fontWeight: 700 }}>{bot.handle}</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>{bot.tagline}</div>
            <p className="muted-copy" style={{ marginTop: 2, fontSize: 12.5 }}>{bot.responsibility}</p>
          </div>
        ))}
      </div>
    )}

    {page.spaces && (
      <div style={{ display: 'grid', gap: 8 }}>
        {page.spaces.map((space) => (
          <a key={space.name} className="feature-row" href={space.link} target="_blank" rel="noreferrer">
            <span style={{ minWidth: 0 }}>
              <strong>{space.name}</strong>
              <span>{space.role}</span>
            </span>
            <span className="feature-row-arrow">→</span>
          </a>
        ))}
      </div>
    )}

    {page.note && <p className="muted-copy" style={{ fontSize: 12.5, fontStyle: 'italic' }}>{page.note}</p>}
  </>
);

export const TourOverlay: React.FC<TourOverlayProps> = ({ tour, canEarnXp, rawInitData, onClose, onFinish }) => {
  const pages = tour?.pages ?? [];
  const [index, setIndex] = useState(0);
  const [dismissed, setDismissed] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [result, setResult] = useState<TourCompleteResult | null>(null);
  const [finishError, setFinishError] = useState(false);

  const page = pages[index];

  const handleFinish = async () => {
    setFinishing(true);
    setFinishError(false);
    let final: TourCompleteResult;
    if (!canEarnXp) {
      final = { status: 'already_completed', xpAwarded: 0 };
    } else {
      final = await completeCommunityTour(rawInitData);
    }
    setFinishing(false);
    setResult(final);
    setFinishError(final.status === 'error');
    onFinish(final);
    markTourAsSeen();
  };

  const handleDismiss = () => {
    markTourAsSeen();
    setDismissed(true);
    onClose();
  };

  if (dismissed || !page) return null;

  const isLast = index === pages.length - 1;
  const shownResult = result;

  return (
    <div
      onClick={handleDismiss}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 1200,
        display: 'flex',
        alignItems: 'flex-end',
        padding: 12,
        background: 'rgba(31, 23, 43, 0.42)',
      }}
    >
      <div
        onClick={(event) => event.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: 496,
          margin: '0 auto',
          background: 'var(--surface)',
          border: '1px solid var(--slate-200)',
          borderRadius: '24px 24px 18px 18px',
          boxShadow: '0 24px 48px rgba(31, 23, 43, 0.28)',
          padding: 18,
          display: 'grid',
          gap: 14,
        }}
      >
        {shownResult ? (
          /* ------------------- FINISH SCREEN ------------------- */
          <div style={{ display: 'grid', gap: 12, textAlign: 'center', paddingTop: 8 }}>
            <span style={{ fontSize: 40 }}>{shownResult.status === 'completed' ? '🎉' : '🧭'}</span>
            {shownResult.status === 'completed' && (
              <>
                <h2 style={{ margin: 0, fontSize: 22 }}>You're in the family!</h2>
                <p className="muted-copy" style={{ fontSize: 13 }}>
                  You've been awarded <strong style={{ color: 'var(--primary-purple)' }}>+{shownResult.xpAwarded} YP</strong> and{' '}
                  <strong style={{ color: 'var(--primary-purple)' }}>+50 Trust Points</strong> for completing your orientation.
                </p>
              </>
            )}
            {shownResult.status === 'already_completed' && (
              <>
                <h2 style={{ margin: 0, fontSize: 22 }}>Orientation confirmed</h2>
                <p className="muted-copy" style={{ fontSize: 13 }}>
                  You already completed your YouThopia orientation. Great to refresh your memory!
                </p>
              </>
            )}
            {shownResult.status === 'error' && (
              <>
                <h2 style={{ margin: 0, fontSize: 22 }}>Tour complete</h2>
                <p className="muted-copy" style={{ fontSize: 13 }}>
                  We couldn't save your orientation just now — your welcome boost will be waiting the next time you visit.
                </p>
              </>
            )}
            <button className="primary-button" onClick={onClose} style={{ marginTop: 6, width: '100%' }}>Done</button>
          </div>
        ) : (
          /* ------------------- TOUR PAGES ------------------- */
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
              <Pill color="purple">Page {index + 1} of {pages.length}</Pill>
              <button
                onClick={handleDismiss}
                aria-label="Close tour"
                style={{ width: 44, height: 44, margin: -6, border: '1px solid var(--slate-200)', borderRadius: '50%', background: '#fff', color: 'var(--text-secondary)', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'grid', gap: 13, maxHeight: 'min(56vh, 430px)', overflowY: 'auto' }}>
              <h2 style={{ margin: 0, fontSize: 23 }}>{page.heading}</h2>
              <div key={page.id} className="tab-enter" style={{ display: 'grid', gap: 12 }}>
                {renderPage(page)}
              </div>
            </div>

            <div style={{ borderTop: '1px solid var(--slate-100)', paddingTop: 13, display: 'grid', gap: 10 }}>
              <div style={{ display: 'flex', gap: 5, justifyContent: 'center' }}>
                {pages.map((_, dotIndex) => (
                  <span
                    key={dotIndex}
                    style={{
                      width: dotIndex === index ? 18 : 7,
                      height: 7,
                      borderRadius: 99,
                      background: dotIndex === index ? 'var(--primary-purple)' : 'var(--purple-100)',
                      transition: 'width 0.2s var(--ease)',
                    }}
                  />
                ))}
              </div>
              <div style={{ display: 'flex', gap: 9 }}>
                {index > 0 && (
                  <button className="secondary-button" onClick={() => setIndex((i) => i - 1)} disabled={finishing} style={{ flex: 1, minHeight: 42 }}>
                    Back
                  </button>
                )}
                {!isLast ? (
                  <button className="primary-button" onClick={() => setIndex((i) => i + 1)} disabled={finishing} style={{ flex: 1, minHeight: 42 }}>
                    Next
                  </button>
                ) : (
                  <button className="primary-button" onClick={handleFinish} disabled={finishing || finishError} style={{ flex: 1, minHeight: 42 }}>
                    {finishing ? 'Finishing…' : 'Finish Tour'}
                  </button>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
