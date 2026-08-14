import React from 'react';

const App: React.FC = () => {
  return (
    <div style={{ padding: '20px', maxWidth: '480px', margin: '0 auto' }}>
      <header style={{ textAlign: 'center', marginBottom: '24px' }}>
        <h1 style={{ color: 'var(--primary-purple)', fontSize: '24px', margin: '0 0 8px 0' }}>
          YouThopiaOS
        </h1>
        <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>
          Christian Community Operating System
        </p>
      </header>

      <div
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--card-border)',
          borderRadius: '16px',
          padding: '20px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        }}
      >
        <h2 style={{ fontSize: '18px', margin: '0 0 12px 0' }}>👋 Welcome to YouThopiaOS</h2>
        <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>
          This is the central visual home for YOUTHOPIA BIBLE COMMUNITY.
        </p>
      </div>
    </div>
  );
};

export default App;
