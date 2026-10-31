"use client";
export function FleetMeshRetryPanel({ requests, retries, retryRate, excessive }: { requests: number; retries: number; retryRate: number; excessive: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Mesh Retries</h3>
    <div className="text-sm">{retries.toLocaleString()} retries / {requests.toLocaleString()} req ({retryRate}%)</div>
    {excessive && <span className="text-xs text-red-500">⚠️ Excessive retries</span>}
  </div>);
}
