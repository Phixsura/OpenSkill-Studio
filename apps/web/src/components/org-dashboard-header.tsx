"use client";

interface OrgDashboardHeaderProps { activeApps: number; totalExecutions: number; errorRate: number; health: string; pendingUpgrades: number; }

const HEALTH_ICONS: Record<string, string> = { healthy: "💚", degraded: "⚠️", critical: "🚨" };

export function OrgDashboardHeader({ activeApps, totalExecutions, errorRate, health, pendingUpgrades }: OrgDashboardHeaderProps) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
      {[
        { label: "Active Apps", value: activeApps, icon: "📦" },
        { label: "Executions", value: totalExecutions.toLocaleString(), icon: "⚡" },
        { label: "Error Rate", value: `${errorRate}%`, icon: errorRate < 5 ? "✅" : "⚠️" },
        { label: "Health", value: health, icon: HEALTH_ICONS[health] ?? "❓" },
        { label: "Upgrades", value: pendingUpgrades, icon: pendingUpgrades > 0 ? "🆕" : "✅" },
      ].map(s => (
        <div key={s.label} className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <span className="text-xl">{s.icon}</span>
          <p className="text-lg font-bold">{s.value}</p>
          <p className="text-xs text-gray-500">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
