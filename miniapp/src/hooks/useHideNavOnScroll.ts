import { useEffect, useRef, useState } from 'react';

/**
 * Returns true while the bottom navigation should be tucked away.
 *
 * The panel hides when the member scrolls down (to give content full height) and
 * slides back on any scroll up. It is always shown near the top of the page and
 * pinned open once the member reaches the bottom, so it is never lost.
 *
 * Reads are throttled to one per animation frame to keep scrolling smooth.
 */
export function useHideNavOnScroll(threshold = 8): boolean {
  const [hidden, setHidden] = useState(false);
  const lastY = useRef(0);
  const ticking = useRef(false);

  useEffect(() => {
    lastY.current = window.scrollY;

    const update = () => {
      ticking.current = false;
      const y = window.scrollY;
      const delta = y - lastY.current;
      const nearTop = y <= 24;
      const nearBottom =
        y + window.innerHeight >= document.documentElement.scrollHeight - 4;

      if (nearTop || nearBottom) {
        setHidden(false);
      } else if (delta > threshold) {
        setHidden(true);
      } else if (delta < -threshold) {
        setHidden(false);
      }

      lastY.current = y;
    };

    const onScroll = () => {
      if (ticking.current) return;
      ticking.current = true;
      window.requestAnimationFrame(update);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, [threshold]);

  return hidden;
}
