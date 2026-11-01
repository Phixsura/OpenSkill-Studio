"use client";

interface Consumer { id: string; healthScore: number; errorRate: number; avgMs: number; status: string; }
interface Props { totalConsumers: number; healthy: number; degraded: number; critical: number; avgScore: number; overall: string; topIssues: string[]; worstConsumers: Consumer[]; appName: string; }

const overallColors: Record<string, string> = { healthy: "bg-green-100 text-green-700", degraded: "bg-amber-100 text-amber-700", critical: "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKConsumerApiPlatformHealthAggregatorCard({ totalConsumers, healthy, degraded, critical, avgScore, overall, topIssues, worstConsumers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Platform Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalConsumers} consumers</p>
        </div>
        <div className="text-right">
          <div className={`text-lg font-bold ${avgScore >= 80 ? "text-green-600" : avgScore >= 50 ? "text-amber-600" : "text-red-600"}`}>{avgScore}%</div>
          <span className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${overallColors[overall] ?? ""}`}>{overall}</span>
        </div>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{healthy}</div><div className="text-[9px] text-gray-400">Healthy</div></div>
        <div className="rounded bg-amber-50 p-1.5 dark:bg-amber-900/20"><div className="font-bold text-amber-600">{degraded}</div><div className="text-[9px] text-gray-400">Degraded</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{critical}</div><div className="text-[9px] text-gray-400">Critical</div></div>
      </div>
      {topIssues.length > 0 && (
        <div className="mb-2 space-y-0.5">{topIssues.map((issue, i) => <div key={i} className="text-[10px] text-amber-600">⚠️ {issue}</div>)}</div>
      )}
      {worstConsumers.length > 0 && (
        <div className="space-y-0.5">
          <div className="text-[10px] text-gray-400">Needs attention:</div>
          {worstConsumers.slice(0, 3).map((c) => (
            <div key={c.id} className="flex justify-between text-[10px]"><span className="text-gray-600">{c.id}</span><span className="text-red-500">{c.healthScore}%</span></div>
          ))}
        </div>
      )}
    </div>
  );
}
