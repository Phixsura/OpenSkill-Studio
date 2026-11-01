"use client";

interface Badge { id: string; label: string; icon: string; description: string; tier: string; }
interface DeveloperBadgeShelfProps { badges: Badge[]; totalAvailable: number; }

const tierColors: Record<string, string> = {
  bronze: "border-orange-300 bg-orange-50 dark:border-orange-700 dark:bg-orange-900/10",
  silver: "border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-800",
  gold: "border-yellow-400 bg-yellow-50 dark:border-yellow-600 dark:bg-yellow-900/10",
  platinum: "border-purple-400 bg-purple-50 dark:border-purple-600 dark:bg-purple-900/10",
};

export function DeveloperBadgeShelf({ badges, totalAvailable }: DeveloperBadgeShelfProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Badges</h2>
        <span className="text-sm text-gray-400">{badges.length}/{totalAvailable}</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {badges.map(b => (
          <div key={b.id} className={`rounded-lg border p-2.5 text-center ${tierColors[b.tier] ?? ""}`} title={b.description}>
            <span className="text-2xl">{b.icon}</span>
            <p className="mt-0.5 text-xs font-medium">{b.label}</p>
            <p className="text-[10px] uppercase text-gray-400">{b.tier}</p>
          </div>
        ))}
        {badges.length === 0 && <p className="text-sm text-gray-400">No badges yet — keep building!</p>}
      </div>
    </div>
  );
}
