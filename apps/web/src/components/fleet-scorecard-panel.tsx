"use client";
const GC: Record<string, string> = { "A+": "text-green-600", A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", D: "text-red-500" };
export function FleetScorecardPanel({ dimensions, avgScore, top, bottom, grade }: { dimensions: number; avgScore: number; top: string | null; bottom: string | null; grade: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🏅 Platform Scorecard</h3>
    <div className={`text-3xl font-black ${GC[grade] ?? ""}`}>{avgScore} — {grade}</div>
    <div className="text-xs text-gray-400 mt-1">{dimensions} dimensions · 💪 {top} · ⚠️ {bottom}</div>
  </div>);
}
