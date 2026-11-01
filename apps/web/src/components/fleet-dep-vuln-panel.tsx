"use client";
export function FleetDepVulnPanel({ totalDeps, critical, high, totalCves, clean }: { totalDeps: number; critical: number; high: number; totalCves: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Dep Vulnerabilities</h3>
    {clean ? <span className="text-xs text-green-600">✅ {totalDeps} deps clean</span>
     : <span className="text-xs text-red-500">⚠️ {totalCves} CVEs · {critical} critical · {high} high</span>}
  </div>);
}
