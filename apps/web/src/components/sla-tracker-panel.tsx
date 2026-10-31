"use client";
interface SlaInfo { service: string; compliant: boolean; uptimePct: number; p99Ms: number; }
interface SlaTrackerPanelProps { services: SlaInfo[]; compliancePct: number; }
export function SlaTrackerPanel({ services, compliancePct }: SlaTrackerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 SLA Compliance</h3>
        <span className={`text-xs font-bold ${compliancePct >= 100 ? "text-green-600" : "text-yellow-600"}`}>{compliancePct}%</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service}</span>
            <span className={s.compliant ? "text-green-600" : "text-red-500"}>{s.compliant ? "✅" : "❌"} {s.uptimePct}% · {s.p99Ms}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
