"use client";
export function FleetStorageClassPanel({ usedGb, allocGb, pct, pressure }: { usedGb: number; allocGb: number; pct: number; pressure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💿 Fleet Storage</h3>
    <div className="text-sm">{usedGb} / {allocGb} GB ({pct}%)</div>
    {pressure && <span className="text-xs text-red-500">⚠️ Storage pressure</span>}
  </div>);
}
