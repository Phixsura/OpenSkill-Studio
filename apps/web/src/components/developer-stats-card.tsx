"use client";

interface DeveloperStatsCardProps {
  appCount: number;
  publishedCount: number;
  totalInstalls: number;
  avgHealthScore: number;
}

export function DeveloperStatsCard({ appCount, publishedCount, totalInstalls, avgHealthScore }: DeveloperStatsCardProps) {
  const stats = [
    { label: "Apps", value: appCount, icon: "📦" },
    { label: "Published", value: publishedCount, icon: "🚀" },
    { label: "Installs", value: totalInstalls, icon: "📥" },
    { label: "Health", value: `${avgHealthScore}%`, icon: avgHealthScore >= 80 ? "💚" : "⚠️" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map(s => (
        <div key={s.label} className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <span className="text-xl">{s.icon}</span>
          <p className="text-xl font-bold">{typeof s.value === "number" ? s.value.toLocaleString() : s.value}</p>
          <p className="text-xs text-gray-500">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
