"use client";

import { useEffect, useState } from "react";

interface PageTransitionWrapperProps { transition: string; durationMs: number;
  show: boolean; children: React.ReactNode; }

const transitionClasses: Record<string, { enter: string; exit: string }> = {
  fade: { enter: "animate-fadeIn", exit: "animate-fadeOut" },
  slide_left: { enter: "animate-slideInRight", exit: "animate-slideOutLeft" },
  slide_up: { enter: "animate-slideInUp", exit: "animate-slideOutDown" },
  scale: { enter: "animate-scaleIn", exit: "animate-scaleOut" },
  none: { enter: "", exit: "" },
};

export function PageTransitionWrapper({ transition, durationMs, show, children }: PageTransitionWrapperProps) {
  const [visible, setVisible] = useState(show);
  const classes = transitionClasses[transition] ?? transitionClasses.fade;

  useEffect(() => {
    if (show) setVisible(true);
    else {
      const timer = setTimeout(() => setVisible(false), durationMs);
      return () => clearTimeout(timer);
    }
  }, [show, durationMs]);

  if (!visible && !show) return null;

  return (
    <div className={`transition-all ${show ? classes.enter : classes.exit}`}
      style={{ animationDuration: `${durationMs}ms` }}>
      {children}
    </div>
  );
}
