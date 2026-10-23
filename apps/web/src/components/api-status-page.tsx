"use client";

interface ServiceStatus { name: string; status: string; uptimePct: number;
  avgLatencyMs: number; errorRatePct: number; icon: string; }
interface ApiStatusPageProps { services: ServiceStatus[]; overall: string;
  avgLatencyMs: number; checkedAt: string; }

const overallLabels: Record<string, { label: string; icon: string }> = {
  operational: { label: "All Systems Operational", icon: "🟢" },
  degraded: { label: "Partial Degradation", icon: "🟡" },
  outage: { label: "Service Outage", icon: "🔴" },
};

export function ApiStatusPage({ services, overall, avgLatencyMs, checkedAt }: ApiStatusPageProps) {
  const o = overallLabels[overall] ?? overallLabels.operational;
  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <div className="rounded-xl border p-5 text-center dark:border-gray-700">
        <span className="text-3xl">{o.icon}</span>
        <h1 className="mt-2 text-xl font-bold">{o.label}</h1>
        <p className="text-xs text-gray-400 mt-1">Avg latency: {avgLatencyMs}ms · Last checked: {new Date(checkedAt).toLocaleTimeString()}</p>
      </div>
      <div className="space-y-2">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between rounded-lg border px-4 py-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{s.icon}</span>
              <span className="text-sm font-medium">{s.name}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{s.uptimePct}%</span>
              <span>{s.avgLatencyMs}ms</span>
              {s.errorRatePct > 0 && <span className="text-red-500">{s.errorRatePct}% err</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
