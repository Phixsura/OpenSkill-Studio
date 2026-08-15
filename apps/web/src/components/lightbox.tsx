"use client";

import { useEffect } from "react";
import { createPortal } from "react-dom";

/**
 * Full-screen image overlay. Closes on Esc, backdrop click, or the ✕ button.
 * Rendered in a portal so it escapes any overflow-clipped ancestors.
 */
export function Lightbox({
  url,
  alt,
  onClose,
}: {
  url: string;
  alt: string;
  onClose: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return createPortal(
    <div
      data-testid="lightbox"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-6"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={alt}
    >
      <button
        type="button"
        aria-label="Close"
        className="absolute right-4 top-4 rounded-full bg-white/10 px-3 py-1 text-lg text-white hover:bg-white/20"
        onClick={onClose}
      >
        ✕
      </button>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={url}
        alt={alt}
        className="max-h-full max-w-full rounded object-contain shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      />
    </div>,
    document.body,
  );
}
