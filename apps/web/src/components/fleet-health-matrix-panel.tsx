"use client";
export function FleetHealthMatrixPanel({ dimensions, avgScore, weakest, strongest, balanced }: { dimensions: number; avgScore: number; weakest: string | null; strongest: string | null; balanced: boolean; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🎯 Health Matrix</h3>
    <div className="text-2xl font-bold">{avgScore}/100</div>
    <div className="text-xs text-gray-400 mt-1">{dimensions} dimensions · 💪 {strongest} · ⚠️ {weakest}</div>
    {!balanced && <div className="text-xs text-yellow-600 mt-1">⚠️ Imbalanced</div>}
  </div>);
}
