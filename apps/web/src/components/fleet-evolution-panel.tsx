"use client";
export function FleetEvolutionPanel({ firstFiles, currentFiles, growthPct, accelerating }: { firstFiles: number; currentFiles: number; growthPct: number; accelerating: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Platform Evolution</h3>
    <div className="text-sm">{firstFiles.toLocaleString()} → {currentFiles.toLocaleString()} files ({growthPct}%)</div>
    {accelerating && <span className="text-xs text-green-600">🚀 Rapid growth!</span>}
  </div>);
}
