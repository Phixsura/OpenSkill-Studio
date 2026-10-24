"use client";

interface Kpi { name: string; value: string; trend: string; }
interface ExecSummaryCardProps { health: string; kpis: Kpi[]; summary: string; }

const HEALTH_COLORS: Record<string, string> = {
  strong: "text-green-600", good: "text-blue-600", at_risk: "text-red-500",
};
const TREND_ICONS: Record<string, string> = { up: "↑", down: "↓", flat: "→", stable: "→" };

export function ExecSummaryCard({ health, kpis, summary }: ExecSummaryCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Executive Summary</h3>
        <span className={`text-xs font-medium capitalize ${HEALTH_COLORS[health] ?? ""}`}>{health.replaceAll("_", " ")}</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {kpis.slice(0, 6).map(k => (
          <div key={k.name} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{k.value} <span className="text-[10px] text-gray-400">{TREND_ICONS[k.trend] ?? ""}</span></div>
            <div className="text-[9px] text-gray-400">{k.name}</div>
          </div>
        ))}
      </div>
      <div className="p-3 text-xs text-gray-500">{summary}</div>
    </div>
  );
}
