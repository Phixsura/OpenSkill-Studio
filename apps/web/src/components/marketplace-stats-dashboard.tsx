"use client";

interface MarketplaceStats {
  totalExtensions: number;
  totalConnectors: number;
  totalDevelopers: number;
  totalInstalls: number;
  newThisWeek: number;
  avgRating: number;
}

interface TrendingExtension {
  id: string;
  name: string;
  author: string;
  category: string;
  installs: number;
  rating: number;
  trend: "up" | "stable" | "new";
}

export function MarketplaceStatsDashboard({
  stats,
  trending,
  categories,
}: {
  stats: MarketplaceStats;
  trending: TrendingExtension[];
  categories: { name: string; count: number }[];
}) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">🏪 Marketplace Overview</h2>

      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
        {[
          { label: "Extensions", value: stats.totalExtensions, icon: "📦" },
          { label: "Connectors", value: stats.totalConnectors, icon: "🔌" },
          { label: "Developers", value: stats.totalDevelopers, icon: "👩‍💻" },
          { label: "Installs", value: stats.totalInstalls, icon: "⬇️" },
          { label: "New This Week", value: stats.newThisWeek, icon: "🆕" },
          { label: "Avg Rating", value: stats.avgRating.toFixed(1), icon: "⭐" },
        ].map((s) => (
          <div key={s.label} className="rounded-lg border dark:border-gray-700 p-3 text-center">
            <div className="text-xl">{s.icon}</div>
            <div className="text-lg font-bold">{typeof s.value === "number" ? s.value.toLocaleString() : s.value}</div>
            <div className="text-xs text-gray-500">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border dark:border-gray-700 p-4">
          <h3 className="font-semibold mb-3">🔥 Trending</h3>
          <div className="space-y-2">
            {trending.map((ext, i) => (
              <div key={ext.id} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 w-5">{i + 1}.</span>
                  <span className="font-medium">{ext.name}</span>
                  <TrendBadge trend={ext.trend} />
                </div>
                <div className="flex items-center gap-3 text-gray-400 text-xs">
                  <span>⬇ {ext.installs.toLocaleString()}</span>
                  <span>★ {ext.rating.toFixed(1)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border dark:border-gray-700 p-4">
          <h3 className="font-semibold mb-3">📂 Categories</h3>
          <div className="space-y-2">
            {categories.map((cat) => (
              <div key={cat.name} className="flex items-center justify-between text-sm">
                <span>{cat.name}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full bg-blue-500"
                      style={{ width: `${Math.min(100, (cat.count / Math.max(...categories.map(c => c.count))) * 100)}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400 w-8 text-right">{cat.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function TrendBadge({ trend }: { trend: string }) {
  if (trend === "up") return <span className="text-green-500 text-xs">↑</span>;
  if (trend === "new") return <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 px-1.5 rounded">NEW</span>;
  return null;
}
