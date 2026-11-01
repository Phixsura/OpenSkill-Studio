"use client";
export function FleetAiRetryPolPanel({ policies, active, retries, successRetries, maxAttempts }: { policies: number; active: number; retries: number; successRetries: number; maxAttempts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔁 AI Retry Policy</h3>
    <div className="text-sm">{active}/{policies} active · {retries.toLocaleString()} retries · {successRetries.toLocaleString()} recovered · max {maxAttempts}</div>
  </div>);
}
