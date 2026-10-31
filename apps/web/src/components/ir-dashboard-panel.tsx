"use client";
interface IrDashboardPanelProps { activeCount: number; resolvedToday: number;
  severityCounts: Record<string, number>; primaryOncall: string; escalationNeeded: boolean; }
export function IrDashboardPanel({ activeCount, resolvedToday, severityCounts, primaryOncall, escalationNeeded }: IrDashboardPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${activeCount > 0 ? "bg-red-500" : "bg-green-500"}`}>
        {activeCount > 0 ? `🚨 ${activeCount} ACTIVE INCIDENTS` : "✅ No Active Incidents"}
        {escalationNeeded && " · ESCALATION NEEDED"}
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Active</span><div className={`font-bold text-lg ${activeCount > 0 ? "text-red-500" : ""}`}>{activeCount}</div></div>
        <div><span className="text-gray-400">Resolved</span><div className="font-bold text-green-600 text-lg">{resolvedToday}</div></div>
        <div><span className="text-gray-400">On-Call</span><div className="font-bold text-lg">{primaryOncall}</div></div>
        <div><span className="text-gray-400">P1s</span><div className={`font-bold text-lg ${(severityCounts.P1 ?? 0) > 0 ? "text-red-500" : ""}`}>{severityCounts.P1 ?? 0}</div></div>
      </div>
    </div>
  );
}
