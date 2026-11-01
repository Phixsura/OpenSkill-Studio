"use client";
export function FleetEngEffPanel({ velocity, quality, delivery, score, effective }: { velocity: number; quality: number; delivery: number; score: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Engineering Effectiveness</h3>
    <div className={`text-lg font-bold ${effective ? "text-green-600" : "text-yellow-600"}`}>{score}%</div>
    <div className="text-xs text-gray-400">V:{velocity} Q:{quality} D:{delivery}</div>
  </div>);
}
