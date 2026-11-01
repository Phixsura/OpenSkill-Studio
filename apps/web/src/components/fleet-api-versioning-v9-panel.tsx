"use client";
export function FleetApiVersioningV9Panel({ total, deprecated }: { total: number; deprecated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 API Versioning v9</h3>
    <div className="text-sm">{total} APIs · {deprecated} deprecated</div>
  </div>);
}
