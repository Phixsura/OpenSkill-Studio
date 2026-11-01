"use client";
interface FleetOverviewPanelProps { overall: string; total: number; healthPct: number;
  totalRps: number; byStatus: Record<string, number>; byTier: Record<string, number>; }
const OV_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function FleetOverviewPanel({ overall, total, healthPct, totalRps, byStatus, byTier }: FleetOverviewPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${OV_COLOR[overall] ?? "bg-gray-500"}`}>
        Fleet: {overall.toUpperCase()} · {total} services · {healthPct}% healthy · {totalRps.toLocaleString()} rps
      </div>
      <div className="grid grid-cols-2 gap-3 p-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">By Status</div>
          {Object.entries(byStatus).map(([s, c]) => <div key={s} className="text-gray-500">{s}: {c}</div>)}
        </div>
        <div>
          <div className="text-gray-400 mb-1">By Tier</div>
          {Object.entries(byTier).map(([t, c]) => <div key={t} className="text-gray-500">{t}: {c}</div>)}
        </div>
      </div>
    </div>
  );
}
