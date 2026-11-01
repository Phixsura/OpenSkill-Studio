"use client";

interface BadgeProgress {
  badge: string;
  icon: string;
  tier: string;
  earned: boolean;
  progress: number;
  threshold: number;
  percent: number;
}

const tierColors: Record<string, string> = {
  bronze: "border-orange-400", silver: "border-gray-400",
  gold: "border-yellow-400", platinum: "border-purple-400",
};

export function DeveloperBadgePanel({ badges }: { badges: BadgeProgress[] }) {
  const earned = badges.filter((b) => b.earned).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🏆 Badges</h2>
        <span className="text-sm text-gray-500">{earned}/{badges.length} earned</span>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {badges.map((b) => (
          <div key={b.badge} className={`rounded-xl border-2 p-3 text-center ${b.earned ? tierColors[b.tier] || "border-gray-300" : "border-gray-200 dark:border-gray-700 opacity-50"}`}>
            <span className="text-2xl block">{b.icon}</span>
            <span className="font-semibold text-xs block mt-1">{b.badge}</span>
            <span className="text-xs text-gray-400 capitalize">{b.tier}</span>
            {!b.earned && (
              <div className="mt-1">
                <div className="h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${b.percent}%` }} />
                </div>
                <span className="text-[10px] text-gray-400">{b.progress}/{b.threshold}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
