"use client";
export function FleetAiCtxWinPanel({ managers, active, maxTokens, usage, overflows }: { managers: number; active: number; maxTokens: number; usage: number; overflows: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Context Window</h3>
    <div className="text-sm">{active}/{managers} active · {(maxTokens/1000).toFixed(0)}K max · {usage}% used · {overflows} overflows</div>
  </div>);
}
