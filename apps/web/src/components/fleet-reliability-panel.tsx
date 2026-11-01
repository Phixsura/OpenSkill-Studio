"use client";
const GC: Record<string, string> = { Platinum: "text-purple-600", Gold: "text-yellow-600", Silver: "text-gray-500", Bronze: "text-orange-600" };
export function FleetReliabilityPanel({ score, grade }: { score: number; grade: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🛡️ Reliability Score</h3>
    <div className={`text-3xl font-black ${GC[grade] ?? ""}`}>{score} — {grade}</div>
  </div>);
}
