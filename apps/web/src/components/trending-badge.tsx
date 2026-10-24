"use client";

interface TrendingBadgeProps { rank: number; score: number; }

export function TrendingBadge({ rank, score }: TrendingBadgeProps) {
  const color = rank <= 3 ? "text-orange-600" : rank <= 10 ? "text-blue-600" : "text-gray-500";
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium ${color}`}>
      🔥 #{rank} <span className="opacity-60">({score})</span>
    </span>
  );
}
