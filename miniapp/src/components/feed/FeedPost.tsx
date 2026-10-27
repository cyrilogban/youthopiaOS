import React, { useState } from 'react';
import { isVerseSaved, toggleSavedVerse } from '../../services/savedVerses';
import { copyText, shareText } from '../../services/share';

export type PostType = 'Verse' | 'Affirmation' | 'Prayer' | 'Card';

export interface FeedPostData {
  id: string;
  type: PostType;
  sourceName: string;
  sourceHandle: string;
  timeLabel: string;
  body: string;
  reference?: string;
  translation?: string;
  verseStyle?: boolean;
  visual?: { eyebrow: string; text: string; reference?: string };
  sample?: boolean;
}

const BookIcon = (
  <>
    <path d="M5 19.5A2.5 2.5 0 0 1 7.5 17H20" />
    <path d="M7.5 3H20v19H7.5A2.5 2.5 0 0 1 5 19.5v-14A2.5 2.5 0 0 1 7.5 3z" />
  </>
);

const BookmarkIcon = (
  <path d="M19 21l-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
);

const ShareIcon = (
  <>
    <path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7" />
    <path d="M12 3v13" />
    <path d="M8 7l4-4 4 4" />
  </>
);

const CopyIcon = (
  <>
    <rect x="9" y="9" width="11" height="11" rx="2" />
    <path d="M5 15V5a2 2 0 0 1 2-2h8" />
  </>
);

export const FeedPost: React.FC<{ post: FeedPostData }> = ({ post }) => {
  const [saved, setSaved] = useState(() => isVerseSaved(post.id));
  const [copied, setCopied] = useState(false);

  const plainText = post.reference ? `${post.body}\n${post.reference}` : post.body;

  const onSave = () => {
    const result = toggleSavedVerse({
      id: post.id,
      reference: post.reference ?? post.type,
      text: post.body,
      translation: post.translation ?? '',
      savedAt: Date.now(),
    });
    setSaved(result.saved);
  };

  const onShare = () => {
    void shareText(`${post.type} of the Day`, plainText);
  };

  const onCopy = async () => {
    const ok = await copyText(plainText);
    if (ok) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    }
  };

  return (
    <article className="post">
      <div className="post-head">
        <span className="bot-mark">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {BookIcon}
          </svg>
        </span>
        <div className="post-meta">
          <strong>{post.sourceName}</strong>
          <span>
            {post.sourceHandle} · {post.timeLabel}
          </span>
        </div>
        <span className="post-type">{post.type}</span>
      </div>

      {post.visual ? (
        <div className="post-visual">
          <div className="eyebrow">{post.visual.eyebrow}</div>
          <p>{post.visual.text}</p>
        </div>
      ) : (
        <div className="post-body">
          <p className={post.verseStyle ? 'post-verse' : 'post-text'}>{post.body}</p>
          {post.reference && <div className="post-ref">{post.reference}</div>}
        </div>
      )}



      <div className="post-actions">
        <button className={`post-action${saved ? ' is-active' : ''}`} onClick={onSave} aria-pressed={saved}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill={saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {BookmarkIcon}
          </svg>
          {saved ? 'Saved' : 'Save'}
        </button>
        <button className="post-action" onClick={onShare}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {ShareIcon}
          </svg>
          Share
        </button>
        <button className="post-action" onClick={onCopy}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {CopyIcon}
          </svg>
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
    </article>
  );
};
