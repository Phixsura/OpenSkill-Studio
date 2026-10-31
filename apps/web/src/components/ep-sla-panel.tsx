"use client";
interface EpSla { endpoint: string; compliant: boolean; availabilityPct: number; p99Ms: number; errorRatePct: number; }
interface EpSlaPanelProps { endpoints: EpSla[]; compliancePct: number; }
export function EpSlaPanel({ endpoints, compliancePct }: EpSlaPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Endpoint SLA</h3>
        <span className={`text-xs font-bold ${compliancePct >= 100 ? "text-green-600" : "text-yellow-600"}`}>
          {compliancePct}% compliant
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{e.compliant ? "✅" : "❌"}</span>
              <span className="font-mono">{e.endpoint}</span>
            </div>
            <span className="text-gray-400">{e.availabilityPct}% · {e.p99Ms}ms · {e.errorRatePct}% err</span>
          </div>
        ))}
      </div>
    </div>
  );
}
