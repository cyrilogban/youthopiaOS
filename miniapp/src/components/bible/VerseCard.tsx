import React, { useState } from 'react';
import { getRawInitData } from '../../services/telegram';
import { saveVerse, unsaveVerse, toggleLikeVerse, logShareVerse } from '../../services/api';
import { usfmToDisplayReference } from '../../services/bibleReference';

export interface VerseCardProps {
  id?: string;
  reference: string;
  text: string;
  translation?: string;
  label?: string;
  initialLiked?: boolean;
  initialSaved?: boolean;
  onBookmarkChange?: (saved: boolean) => void;
  onLikeChange?: (liked: boolean) => void;
}

export const VerseCard: React.FC<VerseCardProps> = ({
  reference,
  text,
  translation = 'KJV',
  label,
  initialLiked = false,
  initialSaved = false,
  onBookmarkChange,
  onLikeChange,
}) => {
  const [liked, setLiked] = useState(initialLiked);
  const [saved, setSaved] = useState(initialSaved);
  const [likeBusy, setLikeBusy] = useState(false);
  const [saveBusy, setSaveBusy] = useState(false);
  const [shareFeedback, setShareFeedback] = useState(false);

  const displayRef = usfmToDisplayReference(reference);

  const handleToggleLike = async () => {
    if (likeBusy) return;
    setLikeBusy(true);
    const nextState = !liked;
    setLiked(nextState);
    if (onLikeChange) onLikeChange(nextState);

    try {
      const res = await toggleLikeVerse(getRawInitData(), displayRef);
      if (res.liked !== nextState) {
        setLiked(res.liked);
      }
    } catch {
      setLiked(!nextState);
    } finally {
      setLikeBusy(false);
    }
  };

  const handleToggleSave = async () => {
    if (saveBusy) return;
    setSaveBusy(true);
    const nextState = !saved;
    setSaved(nextState);
    if (onBookmarkChange) onBookmarkChange(nextState);

    try {
      if (nextState) {
        await saveVerse(getRawInitData(), {
          verse_reference: displayRef,
          verse_text: text,
          translation,
        });
      } else {
        await unsaveVerse(getRawInitData(), displayRef);
      }
    } catch {
      setSaved(!nextState);
    } finally {
      setSaveBusy(false);
    }
  };

  const handleShare = () => {
    const rawData = getRawInitData();
    void logShareVerse(rawData, displayRef);

    const shareBody = `"${text}"\n— ${displayRef} (${translation})\n\nYOUTHOPIA BIBLE COMMUNITY\nSharing God's Love All The Way\nhttps://t.me/joinyouthopia`;

    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp?.openTelegramLink) {
      const tgUrl = `https://t.me/share/url?url=${encodeURIComponent('https://t.me/joinyouthopia')}&text=${encodeURIComponent(shareBody)}`;
      (window as any).Telegram.WebApp.openTelegramLink(tgUrl);
    } else if (navigator.share) {
      navigator
        .share({
          title: `${displayRef} - YouThopia`,
          text: shareBody,
        })
        .catch(() => {});
    } else {
      void navigator.clipboard.writeText(shareBody);
      setShareFeedback(true);
      setTimeout(() => setShareFeedback(false), 2000);
    }
  };

  return (
    <article
      style={{
        background: '#FFFFFF',
        color: '#111827',
        borderRadius: '16px',
        padding: '24px 20px 18px',
        border: '1px solid #E5E7EB',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.04)',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        fontFamily: "'Poppins', sans-serif",
      }}
    >
      {/* Top Bar with Community Brand & Optional Category Label */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 10,
          borderBottom: '1px solid #F3F4F6',
          paddingBottom: '12px',
        }}
      >
        <div>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 800,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: '#000000',
              display: 'block',
            }}
          >
            YOUTHOPIA BIBLE COMMUNITY
          </span>
          <span
            style={{
              fontSize: '10px',
              color: '#6B7280',
              fontWeight: 500,
            }}
          >
            Sharing God's Love All The Way
          </span>
        </div>

        {label && (
          <span
            style={{
              fontSize: '10px',
              fontWeight: 700,
              padding: '3px 8px',
              background: '#000000',
              borderRadius: '6px',
              color: '#FFFFFF',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
            }}
          >
            {label}
          </span>
        )}
      </div>

      {/* Verse Text */}
      <div style={{ padding: '6px 2px', minHeight: 80, display: 'flex', alignItems: 'center' }}>
        <p
          style={{
            margin: 0,
            fontSize: text.length > 180 ? '16px' : '18px',
            lineHeight: 1.65,
            fontWeight: 500,
            color: '#111827',
            textAlign: 'center',
            width: '100%',
          }}
        >
          "{text}"
        </p>
      </div>

      {/* Reference & Translation */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center',
          gap: 8,
          borderTop: '1px solid #F3F4F6',
          paddingTop: '12px',
        }}
      >
        <span
          style={{
            fontSize: '14px',
            fontWeight: 700,
            color: '#000000',
            letterSpacing: '0.01em',
          }}
        >
          {displayRef}
        </span>
        <span
          style={{
            fontSize: '11px',
            fontWeight: 700,
            color: '#4B5563',
            padding: '2px 6px',
            borderRadius: '4px',
            background: '#F3F4F6',
            border: '1px solid #E5E7EB',
          }}
        >
          {translation}
        </span>
      </div>

      {/* Three Action Buttons: Love, Bookmark, Share (Minimalist Black & White Icons) */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          paddingTop: 8,
          borderTop: '1px solid #F3F4F6',
        }}
      >
        {/* Love / Like Button */}
        <button
          type="button"
          onClick={handleToggleLike}
          aria-label={liked ? 'Unlike verse' : 'Love verse'}
          style={{
            background: liked ? '#000000' : '#FFFFFF',
            border: '1px solid #D1D5DB',
            borderRadius: '50%',
            width: 42,
            height: 42,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            color: liked ? '#FFFFFF' : '#111827',
          }}
        >
          <svg width="19" height="19" viewBox="0 0 24 24" fill={liked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
          </svg>
        </button>

        {/* Bookmark / Save Button */}
        <button
          type="button"
          onClick={handleToggleSave}
          aria-label={saved ? 'Remove bookmark' : 'Bookmark verse'}
          style={{
            background: saved ? '#000000' : '#FFFFFF',
            border: '1px solid #D1D5DB',
            borderRadius: '50%',
            width: 42,
            height: 42,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            color: saved ? '#FFFFFF' : '#111827',
          }}
        >
          <svg width="19" height="19" viewBox="0 0 24 24" fill={saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 21l-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
        </button>

        {/* Share Button */}
        <button
          type="button"
          onClick={handleShare}
          aria-label="Share verse"
          style={{
            background: '#FFFFFF',
            border: '1px solid #D1D5DB',
            borderRadius: '50%',
            width: 42,
            height: 42,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            color: '#111827',
          }}
        >
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
            <polyline points="16 6 12 2 8 6" />
            <line x1="12" y1="2" x2="12" y2="15" />
          </svg>
        </button>
      </div>

      {shareFeedback && (
        <div style={{ textAlign: 'center', fontSize: 11, color: '#4B5563', fontWeight: 600 }}>
          Verse copied to clipboard!
        </div>
      )}
    </article>
  );
};
