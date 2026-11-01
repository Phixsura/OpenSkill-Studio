"use client";
export function FleetVerStratPanel({ total, consistent }: { total: number; consistent: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 Versioning Strategy</h3>
    <div className="text-sm">{total} APIs</div>
    {consistent ? <span className="text-xs text-green-600">✅ Consistent</span>
     : <span className="text-xs text-yellow-600">⚠️ Mixed strategies</span>}
  </div>);
}
