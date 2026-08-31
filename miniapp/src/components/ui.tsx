import React from 'react';

interface CardProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  hover?: boolean;
  onClick?: () => void;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, style, hover = false, onClick, className = '' }) => {
  return (
    <div
      onClick={onClick}
      className={className}
      style={{
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--slate-200)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-sm)',
        ...(hover
          ? {
              transition: 'transform 0.2s var(--ease), box-shadow 0.2s var(--ease)',
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
            }
          : undefined
      }
      onMouseLeave={
        hover
          ? (e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
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
  color?: 'purple' | 'slate' | 'success' | 'deep';
  style?: React.CSSProperties;
}

export const Pill: React.FC<PillProps> = ({ children, color = 'slate', style }) => {
  const palettes: Record<string, React.CSSProperties> = {
    purple: { color: 'var(--primary-purple)', background: 'var(--purple-50)', border: '1px solid var(--purple-200)' },
    deep: { color: '#ffffff', background: 'var(--primary-purple)' },
    slate: { color: 'var(--text-secondary)', background: 'var(--slate-100)' },
    success: { color: 'var(--success)', background: 'var(--success-bg)', border: '1px solid var(--success-border)' },
  };
  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 600,
        padding: '3px 9px',
        borderRadius: 'var(--radius-full)',
        border: '1px solid transparent',
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
  style?: React.CSSProperties;
}

export const SectionTitle: React.FC<SectionTitleProps> = ({ children, right, style }) => {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, ...style }}>
      <h3 style={{ fontSize: 14, fontWeight: 700, margin: 0, color: 'var(--text-color)' }}>{children}</h3>
      {right}
    </div>
  );
};
