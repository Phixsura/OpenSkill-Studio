"use client";
export function FleetOncallPanel({ rotations, activeOncall, overloaded, healthy }: { rotations: number; activeOncall: number; overloaded: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📟 On-Call</h3>
    <div className="text-sm">{activeOncall} active · {rotations} rotations</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {overloaded} overloaded</span>}
  </div>);
}
