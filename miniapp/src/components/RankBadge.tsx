import React from 'react';

interface RankBadgeProps {
  title?: string;
  emoji?: string;
  color?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const RankBadge: React.FC<RankBadgeProps> = ({
  title = 'YouTopian Seeker',
  emoji = '🌸',
  color = '#D98A95',
  size = 'md',
}) => {
  const isDarkBg = ['#D98A95', '#D4628E', '#B88B97', '#6D597A'].includes(color);
  const textColor = isDarkBg ? '#FFFFFF' : '#1E1B4B';
  const padding = size === 'sm' ? '2px 8px' : size === 'lg' ? '6px 14px' : '4px 10px';
  const fontSize = size === 'sm' ? 11 : size === 'lg' ? 14 : 12;

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        backgroundColor: color,
        color: textColor,
        borderRadius: 'var(--radius-full)',
        padding,
        fontSize,
        fontWeight: 700,
        boxShadow: '0 2px 6px rgba(0,0,0,0.12)',
        border: '1px solid rgba(255,255,255,0.3)',
        whiteSpace: 'nowrap',
        userSelect: 'none',
      }}
    >
      <span>{emoji}</span>
      <span>{title}</span>
    </div>
  );
};
