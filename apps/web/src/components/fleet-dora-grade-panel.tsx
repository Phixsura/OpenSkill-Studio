"use client";
const LC: Record<string, string> = { Elite: "text-green-600", High: "text-blue-500", Medium: "text-yellow-600", Low: "text-red-500" };
export function FleetDoraGradePanel({ overall, score, df, lt, cfr, mttr }: { overall: string; score: number; df: string; lt: string; cfr: string; mttr: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🏆 DORA Overall</h3>
    <div className={`text-3xl font-black ${LC[overall] ?? ""}`}>{overall}</div>
    <div className="text-xs text-gray-400 mt-2">DF:{df} · LT:{lt} · CFR:{cfr} · MTTR:{mttr} · Score:{score}</div>
  </div>);
}
