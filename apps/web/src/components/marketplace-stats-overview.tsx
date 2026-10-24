"use client";

interface MarketplaceStatsOverviewProps {
  appsDisplay: string; devsDisplay: string; installsDisplay: string;
  apiDisplay: string; ratingDisplay: string; reviewsDisplay: string;
  categories: number; growthDisplay: string; health: string; }

export function MarketplaceStatsOverview({ appsDisplay, devsDisplay, installsDisplay,
  apiDisplay, ratingDisplay, reviewsDisplay, categories, growthDisplay, health }: MarketplaceStatsOverviewProps) {
  const stats = [
    { icon: "📱", value: appsDisplay, label: "Apps" },
    { icon: "👩‍💻", value: devsDisplay, label: "Developers" },
    { icon: "📥", value: installsDisplay, label: "Installs" },
    { icon: "📡", value: apiDisplay, label: "API Calls" },
    { icon: "⭐", value: ratingDisplay, label: "Avg Rating" },
    { icon: "💬", value: reviewsDisplay, label: "Reviews" },
  ];
  return (
    <div className="rounded-xl border p-6 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">📊 Marketplace Stats</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{growthDisplay}</span>
          <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 capitalize">{health}</span>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {stats.map(s => (
          <div key={s.label} className="text-center">
            <p className="text-xl mb-0.5">{s.icon}</p>
            <p className="text-xl font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 text-center mt-3">{categories} categories</p>
    </div>
  );
}
