"use client";

interface Badge { label: string; value: string; color: string; }
interface StatusBadgeDisplayProps { badges: Badge[]; title: string; }

export function StatusBadgeDisplay({ badges, title }: StatusBadgeDisplayProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">{title}</h3>
      <div className="flex gap-2 flex-wrap">
        {badges.map(b => (
          <div key={b.label} className="inline-flex rounded overflow-hidden text-xs font-medium">
            <span className="px-2 py-1 bg-gray-600 text-white">{b.label}</span>
            <span className="px-2 py-1 text-white" style={{ backgroundColor: b.color }}>{b.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
