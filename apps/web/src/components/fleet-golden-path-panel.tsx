"use client";
export function FleetGoldenPathPanel({ total, onGoldenPath, offPath, adoptionPct }: { total: number; onGoldenPath: number; offPath: number; adoptionPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✨ Golden Path</h3>
    <div className="text-sm">{onGoldenPath}/{total} on path ({adoptionPct}%)</div>
    {offPath > 0 && <span className="text-xs text-yellow-600">⚠️ {offPath} off golden path</span>}
  </div>);
}
