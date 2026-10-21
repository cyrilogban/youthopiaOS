import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { BOTS, type SwitcherBot, type SwitcherBotId } from '../data/bots';

const Chevron = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
    <path d="m6 9 6 6 6-6" />
  </svg>
);

const Check = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <path d="m5 13 4 4 10-10" />
  </svg>
);

function BotMark({ bot, mark }: { bot: SwitcherBot; mark?: React.ReactNode }) {
  return (
    <span className="bot-mark">
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        {mark ?? bot.icon}
      </svg>
    </span>
  );
}

/**
 * The cross-bot switch sheet: scrim + bottom panel listing the five doors.
 * Controlled so both the identity header and the /home row can open it. The
 * active bot is derived from the URL, so no prop plumbing is needed.
 */
export const BotSwitcherSheet: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const activeId = location.pathname.match(/^\/(theo|lusie|pete|edie|susie)(?:\/|$)/)?.[1] as SwitcherBotId | undefined;

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="switch-sheet-root" role="dialog" aria-modal="true" aria-label="Switch bot">
      <div className="switch-sheet-scrim" onClick={onClose} />
      <div className="switch-sheet">
        <div className="switch-sheet-handle" aria-hidden="true" />
        <h2 className="switch-sheet-title">Switch bot</h2>
        <div className="switch-sheet-list">
          {BOTS.map((bot) => {
            const active = bot.id === activeId;
            return (
              <button
                key={bot.id}
                type="button"
                aria-current={active ? 'page' : undefined}
                className={`switch-row${active ? ' is-active' : ''}`}
                style={active ? { background: bot.accentSoft, borderColor: bot.accent } : undefined}
                onClick={() => {
                  onClose();
                  if (!active) navigate(bot.route);
                }}
              >
                <BotMark bot={bot} />
                <span className="switch-row-copy">
                  <strong>{bot.name}</strong>
                  <span>{bot.handle} · {bot.role}</span>
                </span>
                {active && <span className="switch-row-check" aria-hidden="true">{Check}</span>}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

/**
 * The tappable identity header each bot route already renders, plus a chevron.
 * Tapping it opens the switch sheet, so bot switching needs no permanent chrome.
 */
export const BotIdentityBar: React.FC<{ botId: SwitcherBotId; tag: string; mark?: React.ReactNode }> = ({ botId, tag, mark }) => {
  const [open, setOpen] = useState(false);
  const bot = BOTS.find((b) => b.id === botId);
  if (!bot) return null;

  return (
    <>
      <button
        type="button"
        className="bot-identity is-tappable"
        aria-label={`Switch bot. Current: ${bot.name}`}
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        <BotMark bot={bot} mark={mark} />
        <span className="bot-identity-copy">
          <strong>{bot.name}</strong>
          <span>{bot.handle}</span>
        </span>
        <span className="bot-identity-tag">{tag}</span>
        <span className="bot-identity-chevron" aria-hidden="true">{Chevron}</span>
      </button>
      <BotSwitcherSheet open={open} onClose={() => setOpen(false)} />
    </>
  );
};
