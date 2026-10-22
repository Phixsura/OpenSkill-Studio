"use client";

interface VerificationBadgeProps { level: "none" | "basic" | "verified" | "trusted"; showLabel?: boolean; }

const BADGE_CONFIG = {
  none: { icon: "", label: "", className: "" },
  basic: { icon: "📧", label: "Email Verified", className: "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300" },
  verified: { icon: "✅", label: "Verified Developer", className: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300" },
  trusted: { icon: "⭐", label: "Trusted Developer", className: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300" },
};

export function VerificationBadge({ level, showLabel = true }: VerificationBadgeProps) {
  if (level === "none") return null;
  const cfg = BADGE_CONFIG[level];
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${cfg.className}`}>
      {cfg.icon} {showLabel && cfg.label}
    </span>
  );
}
