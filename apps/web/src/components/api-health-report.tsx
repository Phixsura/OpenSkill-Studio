"use client";

interface ApiHealthReportProps { grade: string; healthPct: number; totalEndpoints: number;
  healthy: number; degraded: number; unhealthy: number; totalRps: number;
  avgLatencyMs: number; avgErrorRate: number; }

const GRADE_COLORS: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-red-600" };

export function ApiHealthReport({ grade, healthPct, totalEndpoints, healthy, degraded, unhealthy, totalRps, avgLatencyMs, avgErrorRate }: ApiHealthReportProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</div>
        <div className="text-sm text-gray-400 mt-1">API Health · {healthPct}%</div>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Endpoints", v: totalEndpoints }, { l: "RPS", v: totalRps.toLocaleString() },
          { l: "Avg Latency", v: `${avgLatencyMs}ms` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-4 p-3 text-xs">
        <span className="text-green-600">✅ {healthy} healthy</span>
        {degraded > 0 && <span className="text-yellow-600">⚠ {degraded} degraded</span>}
        {unhealthy > 0 && <span className="text-red-500">❌ {unhealthy} unhealthy</span>}
      </div>
    </div>
  );
}
