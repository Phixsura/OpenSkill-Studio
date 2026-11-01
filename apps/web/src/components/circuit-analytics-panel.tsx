"use client";
interface CircuitSvc { service: string; trips: number; recoveries: number; avgOpenMs: number; }
interface CircuitAnalyticsPanelProps { services: CircuitSvc[]; totalTrips: number; flapping: number; mttrMs: number; }
export function CircuitAnalyticsPanel({ services, totalTrips, flapping, mttrMs }: CircuitAnalyticsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Circuit Analytics</h3>
        <span className="text-xs text-gray-400">{totalTrips} trips · MTTR {mttrMs}ms{flapping > 0 ? ` · ⚠ ${flapping} flapping` : ""}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service}</span>
            <span className="text-gray-400">{s.trips} trips · {s.recoveries} recoveries · avg {s.avgOpenMs}ms open</span>
          </div>
        ))}
      </div>
    </div>
  );
}
