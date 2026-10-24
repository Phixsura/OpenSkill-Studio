"use client";

interface InstalledAppCardProps { appName: string; category: string; version: string; status: string; healthScore: number; healthStatus: string; installedAt: string; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊" };
const HEALTH_ICONS: Record<string, string> = { healthy: "💚", degraded: "⚠️", critical: "🚨" };

export function InstalledAppCard({ appName, category, version, status, healthScore, healthStatus, installedAt }: InstalledAppCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span>{ICONS[category] ?? "📦"}</span>
          <div>
            <h4 className="font-semibold">{appName}</h4>
            <p className="text-xs text-gray-500">v{version} · {status}</p>
          </div>
        </div>
        <span title={`${healthScore}%`}>{HEALTH_ICONS[healthStatus] ?? "❓"} {healthScore}%</span>
      </div>
      <p className="mt-2 text-xs text-gray-400">Installed {installedAt}</p>
    </div>
  );
}
