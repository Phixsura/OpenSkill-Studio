"use client";
interface EpSlo { endpoint: string; p99Ms: number; targetMs: number; met: boolean; headroomMs: number; }
interface LatencySloPanelProps { endpoints: EpSlo[]; compliancePct: number; met: number; breached: number; }
export function LatencySloPanelComponent({ endpoints, compliancePct, met, breached }: LatencySloPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Latency SLO</h3>
        <span className={`text-xs font-bold ${breached > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {compliancePct}% compliant · {met} met · {breached} breached
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{e.met ? "✅" : "❌"}</span>
              <span className="font-mono">{e.endpoint}</span>
            </div>
            <span className="text-gray-400">{e.p99Ms}ms / {e.targetMs}ms{e.met ? ` (+${e.headroomMs}ms)` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
