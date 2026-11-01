"use client";
export function FleetApiVerPanel({ total, deprecated, needsMigration }: { total: number; deprecated: number; needsMigration: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 API Versions</h3>
    <div className="text-sm">{total} APIs</div>
    {needsMigration && <span className="text-xs text-yellow-600">⚠️ {deprecated} deprecated APIs need migration</span>}
  </div>);
}
