"use client";

interface SLAInfo { service_name: string; uptime_target: number; current_uptime: number; latency_target_ms: number; current_p95_ms: number; sla_met: boolean; }
interface Props { slas: SLAInfo[]; appName: string; }

export default function APIDeveloperAPISLATrackerCard({ slas, appName }: Props) {
  const violations = slas.filter((s) => !s.sla_met).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 SLA Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{slas.length} SLAs</span>
          {violations > 0 && <p className="text-[10px] text-red-500">{violations} violated</p>}
        </div>
      </div>
      {slas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SLAs configured</p>
      ) : (
        <div className="space-y-1.5">
          {slas.map((s) => (
            <div key={s.service_name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${s.sla_met ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{s.service_name}</span>
              </div>
              <span className="text-gray-400">{s.current_uptime}% / {s.uptime_target}% · {s.current_p95_ms}ms / {s.latency_target_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
