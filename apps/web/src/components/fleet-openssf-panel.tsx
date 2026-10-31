"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600" };
export function FleetOpenSSFPanel({ total, avgScore, lowScore, grade }: { total: number; avgScore: number; lowScore: number; grade: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ OpenSSF</h3>
    <div className={`text-lg font-bold ${GC[grade] ?? ""}`}>{avgScore}/10 — {grade}</div>
    {lowScore > 0 && <span className="text-xs text-yellow-600">⚠️ {lowScore} below 5</span>}
  </div>);
}
