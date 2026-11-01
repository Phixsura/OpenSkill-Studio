"use client";

interface CostPerReqWidgetProps { costPer1k: number; costPerMillion: number;
  totalCost: number; totalRequests: number; improving: boolean | null; pctChange: number | null; }

export function CostPerReqWidget({ costPer1k, costPerMillion, totalCost, totalRequests, improving, pctChange }: CostPerReqWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💲 Cost Per Request</h3>
        {improving !== null && pctChange !== null && (
          <span className={`text-xs ${improving ? "text-green-600" : "text-red-500"}`}>
            {improving ? "↓" : "↑"} {Math.abs(pctChange)}%
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Per 1K", v: `$${costPer1k}` }, { l: "Per 1M", v: `$${costPerMillion}` },
          { l: "Total Cost", v: `$${totalCost.toLocaleString()}` },
          { l: "Requests", v: totalRequests >= 1_000_000 ? `${(totalRequests/1_000_000).toFixed(1)}M` : totalRequests.toLocaleString() }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
