"use client";

interface TrustBadge { id: string; icon: string; label: string; color: string; }
interface TrustBadgeRowProps { badges: TrustBadge[]; trustLevel: string; trustScore: number; }

const LEVEL_STYLE: Record<string, string> = {
  high: "text-green-600", medium: "text-yellow-600", low: "text-gray-400",
};

export function TrustBadgeRow({ badges, trustLevel, trustScore }: TrustBadgeRowProps) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      {badges.map(b => (
        <span key={b.id} className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800"
              title={b.label}>
          {b.icon} {b.label}
        </span>
      ))}
      <span className={`text-xs font-medium ${LEVEL_STYLE[trustLevel] || ""}`}>
        Trust: {trustScore}%
      </span>
    </div>
  );
}
