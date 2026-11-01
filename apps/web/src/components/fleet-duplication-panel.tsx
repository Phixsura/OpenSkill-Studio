"use client";
export function FleetDuplicationPanel({ duplicationPct, clones, acceptable }: { duplicationPct: number; clones: number; acceptable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Code Duplication</h3>
    <div className={`text-lg font-bold ${acceptable ? "text-green-600" : "text-yellow-600"}`}>{duplicationPct}%</div>
    <div className="text-xs text-gray-400">{clones} clones detected</div>
  </div>);
}
