"use client";

interface TrendingApp { id: string; name: string; icon: string; category: string;
  growthPct: number; velocity: number; rating: number; }
interface TrendingAppsProps { apps: TrendingApp[]; period: string; onSelect: (id: string) => void; }

export function TrendingApps({ apps, period, onSelect }: TrendingAppsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔥 Trending</h2>
        <span className="text-xs text-gray-400">{period}</span>
      </div>
      <div className="space-y-2">
        {apps.map((a, i) => (
          <button key={a.id} onClick={() => onSelect(a.id)}
            className="flex w-full items-center gap-3 rounded-xl border p-3 text-left hover:shadow dark:border-gray-700">
            <span className="w-6 text-center text-sm font-bold text-gray-400">#{i + 1}</span>
            <span className="text-2xl">{a.icon}</span>
            <div className="flex-1">
              <p className="text-sm font-semibold">{a.name}</p>
              <p className="text-xs text-gray-400 capitalize">{a.category} · ⭐ {a.rating}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-bold text-green-600">↑ {a.growthPct}%</p>
              <p className="text-xs text-gray-400">{a.velocity}/day</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
