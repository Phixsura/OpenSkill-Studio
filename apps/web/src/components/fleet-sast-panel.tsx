"use client";
export function FleetSastPanel({ scans, totalFindings, critical, high, secure }: { scans: number; totalFindings: number; critical: number; high: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 SAST Results</h3>
    {secure ? <span className="text-xs text-green-600">✅ {scans} scans clean</span>
     : <span className="text-xs text-red-500">⚠️ {totalFindings} findings · {critical} critical · {high} high</span>}
  </div>);
}
