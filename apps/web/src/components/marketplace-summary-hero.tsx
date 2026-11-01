"use client";

interface SummaryStats {
  totalExtensions: number; totalDevelopers: number; totalInstalls: number;
  totalReviews: number; avgRating: number; categories: number; connectors: number;
}

const stats = [
  { key: "totalExtensions" as const, label: "Extensions", icon: "🧩" },
  { key: "totalDevelopers" as const, label: "Developers", icon: "👨‍💻" },
  { key: "totalInstalls" as const, label: "Installs", icon: "📥" },
  { key: "totalReviews" as const, label: "Reviews", icon: "⭐" },
  { key: "connectors" as const, label: "Connectors", icon: "🔗" },
  { key: "categories" as const, label: "Categories", icon: "📂" },
];

export function MarketplaceSummaryHero({ summary }: { summary: SummaryStats }) {
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-xl font-extrabold">OpenSkill Marketplace</h2>
        <p className="text-sm text-gray-500">Discover, install, and build extensions</p>
        <div className="flex items-center justify-center gap-1 mt-1">
          <span className="text-yellow-500">{"★".repeat(Math.round(summary.avgRating))}</span>
          <span className="text-xs text-gray-500">{summary.avgRating.toFixed(1)} avg rating</span>
        </div>
      </div>
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
        {stats.map(s => (
          <div key={s.key} className="border dark:border-gray-700 rounded-xl p-3 text-center">
            <span className="text-lg block">{s.icon}</span>
            <span className="text-lg font-bold block">{summary[s.key].toLocaleString()}</span>
            <span className="text-[10px] text-gray-500">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
