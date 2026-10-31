"use client";
interface SvcCost { service: string; cost: number; sharePct: number; team: string; }
interface SvcCostReportPanelProps { services: SvcCost[]; totalCost: number; }
export function SvcCostReportPanel({ services, totalCost }: SvcCostReportPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Service Costs</h3>
        <span className="text-xs text-gray-400">${totalCost.toLocaleString()}/mo · {services.length} services</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service} <span className="text-gray-400">({s.team})</span></span>
            <span className="text-gray-400">${s.cost} ({s.sharePct}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
