"use client";
export function FleetAiTokCountPanel({ counters, active, inputTokens, outputTokens, cost }: { counters: number; active: number; inputTokens: number; outputTokens: number; cost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 AI Token Counter</h3>
    <div className="text-sm">{active}/{counters} active · {inputTokens.toLocaleString()} in · {outputTokens.toLocaleString()} out · ${cost.toLocaleString()}</div>
  </div>);
}
