"use client";
const LC: Record<string, string> = { Expert: "text-green-600", Advanced: "text-blue-500", Intermediate: "text-yellow-600", Beginner: "text-red-500" };
export function FleetMaturityPanel({ score, level }: { score: number; level: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🏅 Platform Maturity</h3>
    <div className={`text-3xl font-black ${LC[level] ?? ""}`}>{score} — {level}</div>
  </div>);
}
