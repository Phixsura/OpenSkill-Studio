"use client";
interface EndpointCost { endpoint: string; requests: number; cost: number; costPer1k: number; sharePct: number; }
interface CostPerReqPanelProps { endpoints: EndpointCost[]; costPer1k: number; costPerMillion: number; }
export function CostPerReqPanel({ endpoints, costPer1k, costPerMillion }: CostPerReqPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💲 Cost per Request</h3>
        <span className="text-xs text-gray-400">${costPer1k}/1K reqs · ${costPerMillion}/M</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(ep => (
          <div key={ep.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{ep.endpoint}</span>
            <span className="text-gray-400">${ep.cost} ({ep.sharePct}%) · ${ep.costPer1k}/1K</span>
          </div>
        ))}
      </div>
    </div>
  );
}
