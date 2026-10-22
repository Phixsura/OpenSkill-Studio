"use client";

interface MarketplaceStatsCardProps {
  totalApps: number;
  publishedApps: number;
  totalDevelopers: number;
  totalInstallations: number;
}

export function MarketplaceStatsCard({ totalApps, publishedApps, totalDevelopers, totalInstallations }: MarketplaceStatsCardProps) {
  const stats = [
    { label: "Published Apps", value: publishedApps, icon: "📦" },
    { label: "Developers", value: totalDevelopers, icon: "👩‍💻" },
    { label: "Installations", value: totalInstallations, icon: "📥" },
    { label: "Total Apps", value: totalApps, icon: "📊" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map(s => (
        <div key={s.label} className="rounded-lg border border-gray-200 p-4 text-center dark:border-gray-700">
          <span className="text-2xl">{s.icon}</span>
          <p className="mt-1 text-2xl font-bold">{s.value.toLocaleString()}</p>
          <p className="text-xs text-gray-500">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
