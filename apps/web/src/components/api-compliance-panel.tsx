"use client";
interface ComplianceResult { endpoint: string; compliant: boolean; issueCount: number; }
interface ApiCompliancePanelProps { results: ComplianceResult[]; compliancePct: number; total: number; }
export function ApiCompliancePanel({ results, compliancePct, total }: ApiCompliancePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✅ API Compliance</h3>
        <span className={`text-xs font-bold ${compliancePct >= 90 ? "text-green-600" : compliancePct >= 70 ? "text-yellow-600" : "text-red-500"}`}>
          {compliancePct}% compliant · {total} endpoints
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.endpoint}</span>
            <span className={r.compliant ? "text-green-600" : "text-red-500"}>
              {r.compliant ? "✅" : `❌ ${r.issueCount} issues`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
