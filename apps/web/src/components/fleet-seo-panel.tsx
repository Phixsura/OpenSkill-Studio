"use client";
export function FleetSeoPanel({ total, avgScore, poorPages, good }: { total: number; avgScore: number; poorPages: number; good: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 SEO Score</h3>
    <div className={`text-lg font-bold ${good ? "text-green-600" : "text-yellow-600"}`}>{avgScore}/100</div>
    {poorPages > 0 && <span className="text-xs text-yellow-600">⚠️ {poorPages} poor pages</span>}
  </div>);
}
