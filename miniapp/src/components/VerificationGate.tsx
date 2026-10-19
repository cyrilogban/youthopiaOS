import React from 'react';
import type { VerificationState } from '../hooks/useTelegram';

interface VerificationGateProps {
  verification: VerificationState;
  onRetry: () => void | Promise<void>;
  /** TEMPORARY DIAGNOSTIC: initData sourcing snapshot, shown on the blocked screen. */
  diagnostics?: string;
  children: React.ReactNode;
}

const IS_DEV = import.meta.env.DEV;

type BlockedStatus = 'unverified' | 'no-telegram' | 'error';

interface ScreenCopy {
  title: string;
  message: string;
}

function copyFor(status: BlockedStatus): ScreenCopy {
  if (status === 'no-telegram') {
    return {
      title: 'Open inside Telegram',
      message: 'YouThopiaOS lives in Telegram. Open the Mini App from one of our bots to continue.',
    };
  }
  if (status === 'unverified') {
    return {
      title: 'We could not verify you',
      message: 'Your Telegram session did not pass our security check. Relaunch the Mini App from Telegram and try again.',
    };
  }
  return {
    title: 'Something went wrong',
    message: 'We could not reach our servers to confirm your Telegram session. Check your connection and try again.',
  };
}

/**
 * The root trust gate. Every route renders behind this, so a session that the
 * gateway has not verified can never reach member data (Decision 11).
 *
 * - loading: hold the app on a neutral screen while /me resolves.
 * - verified: render the app.
 * - blocked: in production show an explanatory screen with a retry; in local
 *   development fall through so preview mode keeps working without Telegram.
 */
export const VerificationGate: React.FC<VerificationGateProps> = ({ verification, onRetry, diagnostics, children }) => {
  if (verification.status === 'loading') {
    return (
      <div className="verify-screen">
        <div className="verify-card">
          <div className="verify-spinner" aria-hidden="true" />
          <h1>Checking your session</h1>
          <p>Just a moment while we confirm you with Telegram.</p>
        </div>
      </div>
    );
  }

  if (verification.status === 'verified') {
    return <>{children}</>;
  }

  // Local preview: render the app even without a verified session.
  if (IS_DEV) {
    return <>{children}</>;
  }

  const { title, message } = copyFor(verification.status);
  const detail = verification.status === 'unverified' ? verification.detail : undefined;

  return (
    <div className="verify-screen">
      <div className="verify-card">
        <span className="verify-mark" aria-hidden="true">YT</span>
        <h1>{title}</h1>
        <p>{message}</p>
        <button type="button" className="verify-retry" onClick={() => void onRetry()}>
          Try again
        </button>
        <pre
          style={{
            marginTop: 16,
            textAlign: 'left',
            fontSize: 10,
            lineHeight: 1.4,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            color: 'var(--text-muted)',
          }}
        >
          {`DIAG\n${diagnostics ?? ''}\nserver=${detail ?? 'n/a'}`}
        </pre>
      </div>
    </div>
  );
};
