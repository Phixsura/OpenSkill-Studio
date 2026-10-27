"use client";

interface DevStats {
  developerId: string; totalExtensions: number; totalInstalls: number;
  totalReviews: number; avgRating: number; totalRevenueCents: number;
  activeUsers30d: number; topExtension: string;
}

export function DeveloperAnalyticsCard({ stats }: { stats: DevStats }) {
  const metrics = [
    { label: "Extensions", value: stats.totalExtensions, icon: "🧩" },
    { label: "Installs", value: stats.totalInstalls.toLocaleString(), icon: "📥" },
    { label: "Reviews", value: stats.totalReviews.toLocaleString(), icon: "⭐" },
    { label: "Active Users", value: stats.activeUsers30d.toLocaleString(), icon: "👥" },
    { label: "Rating", value: `${stats.avgRating.toFixed(1)}/5`, icon: "🏆" },
    { label: "Revenue", value: `$${(stats.totalRevenueCents / 100).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`, icon: "💰" },
  ];

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Developer Analytics</h3>
      <div className="grid grid-cols-3 gap-2">
        {metrics.map(m => (
          <div key={m.label} className="border dark:border-gray-700 rounded-xl p-3 text-center">
            <span className="text-lg block">{m.icon}</span>
            <span className="text-lg font-bold block">{m.value}</span>
            <span className="text-[10px] text-gray-500">{m.label}</span>
          </div>
        ))}
      </div>
      {stats.topExtension && (
        <div className="text-xs text-gray-500 text-center">Top extension: <span className="font-medium">{stats.topExtension}</span></div>
      )}
    </div>
  );
}
