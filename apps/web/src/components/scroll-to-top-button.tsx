"use client";

import { useState, useEffect } from "react";

interface ScrollToTopButtonProps { showThreshold: number; positionClass: string; smooth: boolean; }

export function ScrollToTopButton({ showThreshold, positionClass, smooth }: ScrollToTopButtonProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handler = () => setVisible(window.scrollY > showThreshold);
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, [showThreshold]);

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: smooth ? "smooth" : "auto" });

  if (!visible) return null;
  return (
    <button onClick={scrollToTop}
      className={`${positionClass} z-40 flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-opacity hover:bg-blue-700`}
      aria-label="Scroll to top">
      ↑
    </button>
  );
}
