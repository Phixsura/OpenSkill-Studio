"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", F: "text-red-500" };
export function FleetHealthScorePanel({ score, grade, services }: { score: number; grade: string; services: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4 text-center">
    <h3 className="font-semibold mb-1">🏆 Fleet Health</h3>
    <div className={`text-2xl font-black ${GC[grade] ?? ""}`}>{score} — {grade}</div>
    <div className="text-xs text-gray-400">{services} services</div>
  </div>);
}
