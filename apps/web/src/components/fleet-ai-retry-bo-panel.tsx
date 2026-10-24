"use client";
export function FleetAiRetryBoPanel({ managers, active, retries, maxBackoff, jitter }: { managers: number; active: number; retries: number; maxBackoff: number; jitter: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔁 AI Retry Backoff</h3>
    <div className="text-sm">{active}/{managers} active · {retries.toLocaleString()} retries · max {maxBackoff}s · {jitter ? "✅" : "❌"} jitter</div>
  </div>);
}
