"use client";
export function FleetStructLogPanel({ total, structured, unstructured, mature }: { total: number; structured: number; unstructured: number; mature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Structured Logging</h3>
    <div className="text-sm">{structured}/{total} structured</div>
    {!mature && <span className="text-xs text-yellow-600">⚠️ {unstructured} unstructured</span>}
  </div>);
}
