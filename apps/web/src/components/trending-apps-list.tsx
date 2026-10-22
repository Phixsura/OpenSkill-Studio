"use client";

interface TrendingApp { name: string; category: string; recentInstalls: number; trendingScore: number; }

interface TrendingAppsListProps { apps: TrendingApp[]; }

const CAT_ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️" };

export function TrendingAppsList({ apps }: TrendingAppsListProps) {
  if (apps.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No trending apps</p>;
  return (
    <div className="space-y-2">
      {apps.map((app, i) => (
        <div key={app.name} className="flex items-center gap-3 rounded border border-gray-200 p-3 dark:border-gray-700">
          <span className="w-6 text-center text-sm font-bold text-gray-400">#{i + 1}</span>
          <span>{CAT_ICONS[app.category] ?? "📦"}</span>
          <span className="flex-1 font-medium">{app.name}</span>
          <span className="text-xs text-gray-500">📥 {app.recentInstalls}</span>
          <span className="text-xs text-blue-600">🔥 {app.trendingScore}</span>
        </div>
      ))}
    </div>
  );
}
