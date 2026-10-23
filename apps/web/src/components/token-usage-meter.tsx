"use client";

interface TokenUsageMeterProps { totalTokens: number; inputTokens: number; outputTokens: number;
  estimatedCost: number; budget: number; pctUsed: number; exceeded: boolean; warning: boolean; }

export function TokenUsageMeter({ totalTokens, inputTokens, outputTokens, estimatedCost,
  budget, pctUsed, exceeded, warning }: TokenUsageMeterProps) {
  const barColor = exceeded ? "bg-red-500" : warning ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Token Usage</h3>
        <span className="text-sm font-bold">${estimatedCost.toFixed(4)}</span>
      </div>
      <div>
        <div className="flex justify-between text-xs text-gray-400">
          <span>{totalTokens.toLocaleString()} / {budget.toLocaleString()}</span>
          <span>{pctUsed}%</span>
        </div>
        <div className="mt-1 h-2.5 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${barColor}`}
            style={{ width: `${Math.min(pctUsed, 100)}%` }} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-center text-xs">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <p className="font-bold">{inputTokens.toLocaleString()}</p>
          <p className="text-gray-400">Input</p>
        </div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <p className="font-bold">{outputTokens.toLocaleString()}</p>
          <p className="text-gray-400">Output</p>
        </div>
      </div>
      {exceeded && <p className="text-center text-xs text-red-500">⚠️ Token budget exceeded</p>}
    </div>
  );
}
