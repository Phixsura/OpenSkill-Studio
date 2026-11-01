"use client";
export function FleetSchemaRegPanel({ total, compatible, breaking, safe }: { total: number; compatible: number; breaking: number; safe: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 Schema Registry</h3>
    {safe ? <span className="text-xs text-green-600">✅ All {total} schemas compatible</span>
     : <span className="text-xs text-red-500">⚠️ {breaking} breaking changes</span>}
  </div>);
}
