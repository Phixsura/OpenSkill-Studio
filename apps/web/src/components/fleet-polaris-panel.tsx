"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600" };
export function FleetPolarisPanel({ total, score, warnings, dangers, grade }: { total: number; score: number; warnings: number; dangers: number; grade: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭐ Polaris</h3>
    <div className={`text-lg font-bold ${GC[grade] ?? ""}`}>{score}% — {grade}</div>
    <div className="text-xs text-gray-400">{warnings} warnings · {dangers} dangers</div>
  </div>);
}
