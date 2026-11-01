"use client";
interface EpCost { endpoint: string; cost: number; costPer1k: number; sharePct: number; }
interface EpCostPanelProps { endpoints: EpCost[]; totalCost: number; }
export function EpCostPanel({ endpoints, totalCost }: EpCostPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💲 Endpoint Costs</h3>
        <span className="text-xs text-gray-400">${totalCost.toLocaleString()} total</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.endpoint}</span>
            <span className="text-gray-400">${e.cost} ({e.sharePct}%) · ${e.costPer1k}/1K</span>
          </div>
        ))}
      </div>
    </div>
  );
}
