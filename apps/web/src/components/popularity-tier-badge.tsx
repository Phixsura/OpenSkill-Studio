"use client";

interface PopularityTierBadgeProps { tier: string; score: number; rank?: number; }

const TIER_STYLE: Record<string, { bg: string; icon: string }> = {
  platinum: { bg: "bg-gradient-to-r from-purple-500 to-indigo-500 text-white", icon: "💎" },
  gold: { bg: "bg-gradient-to-r from-yellow-400 to-amber-500 text-white", icon: "🥇" },
  silver: { bg: "bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800", icon: "🥈" },
  bronze: { bg: "bg-gradient-to-r from-orange-300 to-orange-400 text-white", icon: "🥉" },
};

export function PopularityTierBadge({ tier, score, rank }: PopularityTierBadgeProps) {
  const style = TIER_STYLE[tier] || TIER_STYLE.bronze;
  return (
    <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-medium ${style.bg}`}>
      {style.icon} {tier.charAt(0).toUpperCase() + tier.slice(1)}
      {rank && <span className="opacity-75">#{rank}</span>}
    </span>
  );
}
