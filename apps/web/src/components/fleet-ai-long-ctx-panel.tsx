"use client";
export function FleetAiLongCtxPanel({ managers, active, maxTokens, utilization, requests }: { managers: number; active: number; maxTokens: number; utilization: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Long Context</h3>
    <div className="text-sm">{active}/{managers} active · {(maxTokens/1000).toFixed(0)}K max · {utilization}% util · {requests.toLocaleString()} req</div>
  </div>);
}
