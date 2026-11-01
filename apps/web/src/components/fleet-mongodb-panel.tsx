"use client";
export function FleetMongodbPanel({ members, primary, secondary, maxLag, healthy }: { members: number; primary: number; secondary: number; maxLag: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🍃 MongoDB</h3>
    <div className="text-sm">{primary}P/{secondary}S · lag {maxLag}s</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ Replica set issue</span>}
  </div>);
}
