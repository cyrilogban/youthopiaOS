import React from 'react';

interface CardProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  hover?: boolean;
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, style, hover = false, onClick, className = '' }) => {
  return (
    <div
      onClick={onClick}
      className={className}
      style={{
        background: 'var(--grad-card)',
        border: '1px solid rgba(221, 214, 254, 0.7)',
        borderRadius: 'var(--radius-xl)',
        boxShadow: 'var(--shadow-sm)',
        ...(hover
          ? {
              transition: 'transform 0.2s var(--ease), box-shadow 0.2s var(--ease), border-color 0.2s var(--ease)',
              cursor: onClick ? 'pointer' : undefined,
            }
          : {}),
        ...style,
      }}
      onMouseEnter={
        hover
          ? (e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              e.currentTarget.style.borderColor = 'var(--purple-200)';
            }
          : undefined
      }
      onMouseLeave={
        hover
          ? (e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
              e.currentTarget.style.borderColor = 'rgba(221, 214, 254, 0.7)';
            }
          : undefined
      }
    >
      {children}
    </div>
  );
};

interface SkeletonProps {
  height?: number;
  width?: string | number;
  radius?: number;
  style?: React.CSSProperties;
}

export const Skeleton: React.FC<SkeletonProps> = ({ height = 14, width = '100%', radius = 8, style }) => {
  return <div className="skeleton" style={{ height, width, borderRadius: radius, ...style }} />;
};

interface PillProps {
  children: React.ReactNode;
  color?: 'purple' | 'slate' | 'success' | 'deep' | 'warning' | 'neutral';
  style?: React.CSSProperties;
}

export const Pill: React.FC<PillProps> = ({ children, color = 'slate', style }) => {
  const palettes: Record<string, React.CSSProperties> = {
    purple: { color: 'var(--primary-purple)', background: 'var(--purple-50)', border: '1px solid var(--purple-200)' },
    deep: { color: '#ffffff', background: 'var(--primary-purple)', border: '1px solid var(--primary-purple)' },
    slate: { color: 'var(--text-secondary)', background: 'var(--slate-100)', border: '1px solid var(--slate-200)' },
    neutral: { color: 'var(--text-secondary)', background: 'var(--slate-100)', border: '1px solid var(--slate-200)' },
    success: { color: 'var(--success)', background: 'var(--success-bg)', border: '1px solid var(--success-border)' },
    warning: { color: 'var(--warning)', background: 'var(--warning-bg)', border: '1px solid #fde68a' },
  };

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 5,
        maxWidth: '100%',
        minHeight: 24,
        padding: '3px 9px',
        borderRadius: 'var(--radius-full)',
        fontSize: 11,
        fontWeight: 750,
        whiteSpace: 'nowrap',
        ...palettes[color],
        ...style,
      }}
    >
      {children}
    </span>
  );
};

interface SectionTitleProps {
  children: React.ReactNode;
  right?: React.ReactNode;
  eyebrow?: string;
  style?: React.CSSProperties;
}

export const SectionTitle: React.FC<SectionTitleProps> = ({ children, right, eyebrow, style }) => {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: 12, marginBottom: 12, ...style }}>
      <div>
        {eyebrow && <div className="eyebrow" style={{ marginBottom: 3 }}>{eyebrow}</div>}
        <h3 style={{ fontSize: 15, fontWeight: 850, margin: 0, color: 'var(--text-color)', lineHeight: 1.2 }}>{children}</h3>
      </div>
      {right}
    </div>
  );
};

interface ProgressBarProps {
  value: number;
  max?: number;
  tone?: 'purple' | 'success';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ value, max = 100, tone = 'purple' }) => {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const fill = tone === 'success' ? 'linear-gradient(90deg, #22c55e, #86efac)' : 'linear-gradient(90deg, #8b5cf6, #ffffff)';

  return (
    <div style={{ width: '100%', height: 10, borderRadius: 999, background: 'rgba(255,255,255,0.22)', overflow: 'hidden' }}>
      <div
        style={{
          width: `${pct}%`,
          height: '100%',
          borderRadius: 999,
          background: fill,
          transition: 'width 0.7s var(--ease)',
        }}
      />
    </div>
  );
};
