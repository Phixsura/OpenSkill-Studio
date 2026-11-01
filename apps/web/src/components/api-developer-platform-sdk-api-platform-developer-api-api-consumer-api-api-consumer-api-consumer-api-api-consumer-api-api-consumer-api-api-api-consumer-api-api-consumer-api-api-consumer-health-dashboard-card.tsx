"use client";

interface Indicator { name: string; status: string; value: number; threshold: number; unit: string; }
interface Props { consumerId: string; overallStatus: string; healthScore: number; indicators: Indicator[]; activeAlerts: number; activeIncidents: number; appName: string; }

const statusColors: Record<string, string> = {
  healthy: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  degraded: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};
const statusDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-amber-500", critical: "bg-red-500" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerHealthDashboardCard({ consumerId, overallStatus, healthScore, indicators, activeAlerts, activeIncidents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Health Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-lg font-bold ${healthScore >= 80 ? "text-green-600" : healthScore >= 50 ? "text-amber-600" : "text-red-600"}`}>{healthScore}%</span>
          <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${statusColors[overallStatus] ?? ""}`}>{overallStatus}</span>
        </div>
      </div>
      <div className="mb-3 space-y-1">
        {indicators.map((ind) => (
          <div key={ind.name} className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-1.5">
              <span className={`h-2 w-2 rounded-full ${statusDot[ind.status] ?? ""}`} />
              <span className="text-gray-700 dark:text-gray-300">{ind.name}</span>
            </div>
            <span className="text-gray-500">{ind.value}{ind.unit} (threshold: {ind.threshold}{ind.unit})</span>
          </div>
        ))}
      </div>
      {(activeAlerts > 0 || activeIncidents > 0) && (
        <div className="flex gap-3 text-[10px]">
          {activeAlerts > 0 && <span className="text-amber-500">🔔 {activeAlerts} alerts</span>}
          {activeIncidents > 0 && <span className="text-red-500">🚨 {activeIncidents} incidents</span>}
        </div>
      )}
    </div>
  );
}
