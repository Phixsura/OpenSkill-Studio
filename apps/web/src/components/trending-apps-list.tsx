"use client";

interface TrendingApp { name: string; icon?: string; rating: number;
  recentInstalls: number; trendingScore: number; rank: number; }
interface TrendingAppsListProps { apps: TrendingApp[]; onSelect: (name: string) => void; }

export function TrendingAppsList({ apps, onSelect }: TrendingAppsListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 Trending Apps</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {apps.map(a => (
          <button key={a.name} onClick={() => onSelect(a.name)}
            className="w-full text-left flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
            <span className="text-lg font-bold text-gray-300 w-6">{a.rank}</span>
            <span className="text-xl">{a.icon || "📱"}</span>
            <div className="flex-1">
              <p className="text-sm font-medium">{a.name}</p>
              <div className="flex gap-2 text-xs text-gray-400">
                <span>⭐ {a.rating}</span>
                <span>📥 {a.recentInstalls.toLocaleString()}</span>
              </div>
            </div>
            <span className="text-xs font-mono text-gray-300">{a.trendingScore}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
