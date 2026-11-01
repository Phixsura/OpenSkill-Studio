"use client";

interface ServiceReadiness { service: string; ready: boolean;
  checks: Record<string, boolean>; }
interface ReadinessProbePanelProps { services: ServiceReadiness[]; ready: number;
  total: number; allReady: boolean; }

export function ReadinessProbePanel({ services, ready, total, allReady }: ReadinessProbePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Readiness Probes</h3>
        <span className={`text-xs ${allReady ? "text-green-600" : "text-yellow-600"}`}>
          {allReady ? "✅ All Ready" : `⏳ ${ready}/${total} ready`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="px-4 py-2 text-xs">
            <div className="flex items-center gap-2 mb-0.5">
              <span>{s.ready ? "✅" : "⏳"}</span>
              <span className="font-medium">{s.service}</span>
            </div>
            <div className="flex gap-2 pl-5">
              {Object.entries(s.checks).map(([k, v]) => (
                <span key={k} className={v ? "text-green-600" : "text-red-500"}>{v ? "✓" : "✗"} {k}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
