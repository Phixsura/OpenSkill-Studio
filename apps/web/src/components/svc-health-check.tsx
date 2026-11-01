"use client";

interface HealthResult { service: string; healthy: boolean; checksPassed: number;
  checksTotal: number; latencyMs: number; }
interface SvcHealthCheckProps { results: HealthResult[]; overall: string;
  healthPct: number; healthy: number; unhealthy: number; }

export function SvcHealthCheck({ results, overall, healthPct, healthy, unhealthy }: SvcHealthCheckProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Health Checks</h3>
        <span className={`text-xs ${overall === "healthy" ? "text-green-600" : "text-yellow-600"}`}>
          {overall} · {healthPct}% · {healthy}✓ {unhealthy}✗
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.service} className="flex justify-between px-4 py-2 text-xs">
            <span>{r.healthy ? "✅" : "❌"} {r.service}</span>
            <span className="text-gray-400">{r.checksPassed}/{r.checksTotal} checks · {r.latencyMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
