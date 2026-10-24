"use client";
export function FleetSevDistPanel({ total, sev1Count, critical }: { total: number; sev1Count: number; critical: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Severity Distribution</h3>
    <div className="text-sm">{total} incidents · {sev1Count} SEV1</div>
    {critical && <span className="text-xs text-red-500">🚨 Critical incidents active</span>}
  </div>);
}
