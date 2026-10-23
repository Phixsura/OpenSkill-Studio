"use client";

import { useEffect, useState } from "react";

interface AnimatedTransitionProps { show: boolean; duration?: number; type?: string; children: React.ReactNode; }

export function AnimatedTransition({ show, duration = 300, type = "fade", children }: AnimatedTransitionProps) {
  const [visible, setVisible] = useState(show);
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    if (show) {
      setVisible(true);
      requestAnimationFrame(() => setAnimating(true));
    } else {
      setAnimating(false);
      const timer = setTimeout(() => setVisible(false), duration);
      return () => clearTimeout(timer);
    }
  }, [show, duration]);

  if (!visible) return null;

  const baseClasses = "transition-all";
  const stateClasses = animating ? "opacity-100 translate-y-0 scale-100" : "opacity-0 translate-y-2 scale-95";

  return (
    <div className={`${baseClasses} ${stateClasses}`} style={{ transitionDuration: `${duration}ms` }}>
      {children}
    </div>
  );
}
