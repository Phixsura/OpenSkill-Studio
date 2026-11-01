"use client";

interface Badge { label: string; value: string; color: string; }
interface StatusBadgeDisplayProps { badges: Badge[]; }

const COLORS: Record<string, string> = {
  green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500", blue: "bg-blue-500", gray: "bg-gray-500",
};

export function StatusBadgeDisplay({ badges }: StatusBadgeDisplayProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Status Badges</h3>
      </div>
      <div className="p-4 flex flex-wrap gap-2">
        {badges.map(b => (
          <div key={b.label} className="flex rounded overflow-hidden text-xs text-white">
            <span className="bg-gray-600 px-2 py-0.5">{b.label}</span>
            <span className={`px-2 py-0.5 ${COLORS[b.color] ?? COLORS.gray}`}>{b.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
