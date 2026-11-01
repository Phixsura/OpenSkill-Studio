"use client";

interface TagResult { resource: string; compliant: boolean; missing: string[]; tagCount: number; }
interface InfraTagComplianceProps { results: TagResult[]; compliancePct: number;
  compliant: number; nonCompliant: number; }

export function InfraTagCompliance({ results, compliancePct, compliant, nonCompliant }: InfraTagComplianceProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Tag Compliance</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{compliant} compliant</span>
          {nonCompliant > 0 && <span className="text-red-500">{nonCompliant} non-compliant</span>}
          <span className="text-gray-400">{compliancePct}%</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.resource} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{r.compliant ? "✅" : "❌"}</span>
              <span className="font-mono">{r.resource}</span>
            </div>
            {r.missing.length > 0 && (
              <span className="text-red-500">missing: {r.missing.join(", ")}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
