"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", F: "text-red-500" };
export function FleetDxScorePanel({ score, grade }: { score: number; grade: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🎯 Developer Experience</h3>
    <div className={`text-3xl font-black ${GC[grade] ?? ""}`}>{score} — {grade}</div>
  </div>);
}
