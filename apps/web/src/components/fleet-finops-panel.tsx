"use client";
const LC: Record<string, string> = { Run: "text-green-600", Walk: "text-blue-500", Crawl: "text-yellow-600" };
export function FleetFinopsPanel({ score, level }: { score: number; level: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4 text-center">
    <h3 className="font-semibold mb-1">💰 FinOps</h3>
    <div className={`text-2xl font-black ${LC[level] ?? ""}`}>{score} — {level}</div>
  </div>);
}
