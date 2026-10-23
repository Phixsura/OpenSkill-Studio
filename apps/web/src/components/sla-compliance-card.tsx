"use client";

interface SlaResult { name: string; target: number; actual: number; met: boolean; status: string; }
interface SlaComplianceCardProps { results: SlaResult[]; compliancePct: number; breachedNames: string[]; }

export function SlaComplianceCard({ results, compliancePct, breachedNames }: SlaComplianceCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 SLA Compliance</h3>
        <div className="flex items-center gap-2">
          <span className={`text-lg font-bold ${compliancePct === 100 ? "text-green-600" : "text-yellow-600"}`}>{compliancePct}%</span>
          {breachedNames.length > 0 && <span className="text-xs text-red-500">⚠ {breachedNames.length} breached</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{r.met ? "✅" : "❌"}</span>
              <span className="text-sm font-medium">{r.name}</span>
            </div>
            <div className="text-xs text-gray-400">
              <span className={r.met ? "text-green-600" : "text-red-500"}>{r.actual}%</span>
              <span className="mx-1">/</span>
              <span>{r.target}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
