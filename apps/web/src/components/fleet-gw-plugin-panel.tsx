"use client";
export function FleetGwPluginPanel({ total, active, deprecated, healthy }: { total: number; active: number; deprecated: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 Gateway Plugins</h3>
    <div className="text-sm">{active}/{total} active</div>
    {!healthy && <span className="text-xs text-yellow-600">⚠️ {deprecated} deprecated plugins</span>}
  </div>);
}
