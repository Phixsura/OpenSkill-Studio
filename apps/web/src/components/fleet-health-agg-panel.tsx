"use client";
const SC: Record<string, string> = { healthy: "text-green-600", degraded: "text-yellow-600", critical: "text-red-500" };
export function FleetHealthAggPanel({ overallScore, dimensions, critical, status }: { overallScore: number; dimensions: number; critical: number; status: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🏥 Fleet Health</h3>
    <div className={`text-3xl font-black ${SC[status] ?? ""}`}>{overallScore}</div>
    <div className="text-xs text-gray-400">{dimensions} dimensions · {critical} critical</div>
  </div>);
}
