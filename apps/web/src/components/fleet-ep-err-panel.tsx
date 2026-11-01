"use client";
export function FleetEpErrPanel({ total, noisyEndpoints, worst, worstRate }: { total: number; noisyEndpoints: number; worst: string | null; worstRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 Endpoint Errors</h3>
    <div className="text-sm">{noisyEndpoints}/{total} noisy</div>
    {worst && <div className="text-xs text-red-500">Worst: {worst} ({worstRate}%)</div>}
  </div>);
}
