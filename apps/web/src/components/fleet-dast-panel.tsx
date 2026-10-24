"use client";
export function FleetDastPanel({ scans, totalVulns, critical, secure }: { scans: number; totalVulns: number; critical: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔓 DAST Results</h3>
    {secure ? <span className="text-xs text-green-600">✅ {scans} scans — no critical vulns</span>
     : <span className="text-xs text-red-500">⚠️ {totalVulns} vulns · {critical} critical</span>}
  </div>);
}
