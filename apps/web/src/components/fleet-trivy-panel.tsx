"use client";
export function FleetTrivyPanel({ totalScans, clean, critical, high, allClean }: { totalScans: number; clean: number; critical: number; high: number; allClean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Trivy</h3>
    {allClean ? <span className="text-xs text-green-600">✅ All {totalScans} scans clean</span>
     : <span className="text-xs text-red-500">⚠️ {critical} critical · {high} high across {totalScans} scans</span>}
  </div>);
}
