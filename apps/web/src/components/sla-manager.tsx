"use client";

interface SlaResult { metric: string; target: number; actual: number; met: boolean; }
interface SlaManagerProps { service: string; results: SlaResult[];
  compliancePct: number; fullyCompliant: boolean; }

export function SlaManager({ service, results, compliancePct, fullyCompliant }: SlaManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 SLA: {service}</h3>
        <span className={`text-xs ${fullyCompliant ? "text-green-600" : "text-yellow-600"}`}>
          {fullyCompliant ? "✅ Compliant" : `⚠ ${compliancePct}%`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.metric} className="flex items-center justify-between px-4 py-2 text-xs">
            <span>{r.met ? "✅" : "❌"} {r.metric}</span>
            <span className="font-mono">{r.actual} / {r.target}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
