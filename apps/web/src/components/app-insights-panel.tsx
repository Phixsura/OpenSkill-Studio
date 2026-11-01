"use client";

interface Kpi { label: string; display: string; trend?: string; }
interface AppInsightsPanelProps { appId: string; kpis: Kpi[]; health: string; }

const HEALTH_BADGE: Record<string, string> = {
  excellent: "bg-green-100 text-green-700", good: "bg-blue-100 text-blue-700",
  needs_attention: "bg-yellow-100 text-yellow-700", critical: "bg-red-100 text-red-700",
};

export function AppInsightsPanel({ appId, kpis, health }: AppInsightsPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📊 App Insights</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${HEALTH_BADGE[health] || ""}`}>{health.replace("_", " ")}</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {kpis.map(k => (
          <div key={k.label} className="rounded-lg bg-gray-50 dark:bg-gray-800 p-3 text-center">
            <p className="text-lg font-bold">{k.display}</p>
            <p className="text-xs text-gray-400">{k.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
