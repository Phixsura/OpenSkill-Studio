"use client";

interface Badge { icon: string; label: string; condition: string; }

interface BadgeListProps { badges: Badge[]; }

export function BadgeList({ badges }: BadgeListProps) {
  if (badges.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {badges.map(b => (
        <span key={b.label} className="inline-flex items-center gap-1 rounded-full border border-gray-200 px-2 py-0.5 text-xs dark:border-gray-700" title={b.condition}>
          {b.icon} {b.label}
        </span>
      ))}
    </div>
  );
}
