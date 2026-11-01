"use client";
interface EpBudget { endpoint: string; budget: number; consumed: number; pctConsumed: number; exhausted: boolean; }
interface EpErrorBudgetPanelProps { endpoints: EpBudget[]; exhaustedCount: number; allWithinBudget: boolean; }
export function EpErrorBudgetPanel({ endpoints, exhaustedCount, allWithinBudget }: EpErrorBudgetPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Endpoint Error Budgets</h3>
        <span className={`text-xs font-bold ${allWithinBudget ? "text-green-600" : "text-red-500"}`}>
          {allWithinBudget ? "✅ All within budget" : `❌ ${exhaustedCount} exhausted`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className={`font-mono ${e.exhausted ? "text-red-600 font-bold" : ""}`}>{e.endpoint}</span>
              <span className="text-gray-400">{e.consumed}/{e.budget} ({e.pctConsumed}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${e.exhausted ? "bg-red-500" : e.pctConsumed > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(e.pctConsumed, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
