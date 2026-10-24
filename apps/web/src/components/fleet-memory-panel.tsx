"use client";
export function FleetMemoryPanel({ usedMb, allocMb, pct, pressure }: { usedMb: number; allocMb: number; pct: number; pressure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 Fleet Memory</h3>
    <div className="text-sm">{usedMb.toLocaleString()} / {allocMb.toLocaleString()} MB ({pct}%)</div>
    {pressure && <span className="text-xs text-red-500">⚠️ Memory pressure</span>}
  </div>);
}
