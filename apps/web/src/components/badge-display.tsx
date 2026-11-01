"use client";

interface Badge { id: string; label: string; icon: string; description: string; }
interface BadgeDisplayProps { badges: Badge[]; }

export function BadgeDisplay({ badges }: BadgeDisplayProps) {
  if (badges.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1.5">
      {badges.map(b => (
        <span key={b.id} title={b.description}
          className="flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium dark:border-gray-700 cursor-help">
          <span>{b.icon}</span>{b.label}
        </span>
      ))}
    </div>
  );
}
