"use client";

interface InstallationHealthSummaryProps { total: number; healthy: number; degraded: number; critical: number; overall: string; }

const STATUS_ICONS: Record<string, string> = { healthy: "💚", degraded: "⚠️", critical: "🚨", unknown: "❓" };

export function InstallationHealthSummary({ total, healthy, degraded, critical, overall }: InstallationHealthSummaryProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-xl">{STATUS_ICONS[overall] ?? "❓"}</span>
        <h4 className="font-semibold capitalize">{overall}</h4>
        <span className="text-xs text-gray-500">{total} installations</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <div><p className="text-lg font-bold text-green-600">{healthy}</p><p className="text-xs">Healthy</p></div>
        <div><p className="text-lg font-bold text-yellow-600">{degraded}</p><p className="text-xs">Degraded</p></div>
        <div><p className="text-lg font-bold text-red-600">{critical}</p><p className="text-xs">Critical</p></div>
      </div>
    </div>
  );
}
