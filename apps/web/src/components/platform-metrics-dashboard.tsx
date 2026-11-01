"use client";

interface PlatformMetricsDashboardProps {
  apps: number; developers: number; installations: number; activeUsers: number;
  executions24h: number; errors24h: number; errorRate: number; webhooks24h: number;
  healthStatus: string; avgHealth: number;
}

export function PlatformMetricsDashboard(p: PlatformMetricsDashboardProps) {
  const cards = [
    { label: "Apps", value: p.apps, icon: "📦" },
    { label: "Developers", value: p.developers, icon: "👩‍💻" },
    { label: "Installations", value: p.installations, icon: "📥" },
    { label: "Active Users (7d)", value: p.activeUsers, icon: "👥" },
    { label: "Executions (24h)", value: p.executions24h.toLocaleString(), icon: "⚡" },
    { label: "Error Rate", value: `${p.errorRate}%`, icon: p.errorRate < 5 ? "✅" : "⚠️" },
    { label: "Webhooks (24h)", value: p.webhooks24h.toLocaleString(), icon: "🔔" },
    { label: "Health", value: `${p.avgHealth}%`, icon: p.healthStatus === "healthy" ? "💚" : "⚠️" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {cards.map(c => (
        <div key={c.label} className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <span className="text-xl">{c.icon}</span>
          <p className="text-lg font-bold">{c.value}</p>
          <p className="text-xs text-gray-500">{c.label}</p>
        </div>
      ))}
    </div>
  );
}
