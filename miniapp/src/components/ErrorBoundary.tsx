import React from 'react';

interface ErrorBoundaryState {
  error: Error | null;
}

export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('App crashed:', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, fontFamily: 'sans-serif' }}>
          <h2 style={{ fontSize: 18 }}>Something went wrong</h2>
          <p style={{ color: '#64748b', fontSize: 13 }}>The app hit an unexpected error. Restarting it usually helps.</p>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: 12,
              padding: '10px 18px',
              borderRadius: 999,
              border: '1px solid #6d28d9',
              background: '#6d28d9',
              color: '#fff',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
