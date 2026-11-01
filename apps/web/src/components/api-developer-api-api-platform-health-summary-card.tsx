"use client";

interface HealthInfo {
  api_uptime_pct: number; avg_latency_ms: number; error_rate_pct: number;
  webhook_success_rate_pct: number; webhook_queue_depth: number;
  active_consumers: number; total_api_calls_24h: number;
  security_score: number; open_findings: number;
  services_healthy: number; services_total: number; circuits_open: number;
  overall_health: string; health_score: number;
}
interface Props { health: HealthInfo; appName: string; }

const hBanner: Record<string, string> = { healthy: "bg-green-50 text-green-700 border-green-200", degraded: "bg-yellow-50 text-yellow-700 border-yellow-200", warning: "bg-orange-50 text-orange-700 border-orange-200", critical: "bg-red-50 text-red-700 border-red-200" };

export default function APIDeveloperAPIApiPlatformHealthSummaryCard({ health: h, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-gray-200 bg-white p-5 shadow-lg dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">🏥 Platform Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-2xl font-black text-blue-600">{h.health_score}</span>
      </div>
      <div className={`mb-4 rounded-lg border px-3 py-2 text-center text-[11px] font-bold ${hBanner[h.overall_health] ?? ""}`}>
        {h.overall_health.toUpperCase()}
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "Uptime", v: `${h.api_uptime_pct}%` },
          { l: "Latency", v: `${h.avg_latency_ms}ms` },
          { l: "Errors", v: `${h.error_rate_pct}%` },
          { l: "Webhooks", v: `${h.webhook_success_rate_pct}%` },
          { l: "Queue", v: h.webhook_queue_depth },
          { l: "Consumers", v: h.active_consumers },
          { l: "Calls 24h", v: h.total_api_calls_24h.toLocaleString() },
          { l: "Security", v: h.security_score },
          { l: "Findings", v: h.open_findings },
          { l: "Services", v: `${h.services_healthy}/${h.services_total}` },
          { l: "Circuits", v: h.circuits_open },
          { l: "Score", v: h.health_score },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-400">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
