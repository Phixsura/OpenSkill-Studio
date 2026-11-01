"use client";

interface ComplianceResult { id: string; label: string; required: boolean; met: boolean; status: string; }
interface ComplianceCheckerReportProps { framework: string; compliant: boolean; results: ComplianceResult[]; score: number; }

const statusIcon = (s: string) => s === "pass" ? "✅" : s === "fail" ? "❌" : "⚠️";

export function ComplianceCheckerReport({ framework, compliant, results, score }: ComplianceCheckerReportProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold uppercase">{framework} Compliance</h2>
        <div className="flex items-center gap-2">
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${compliant ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
            {compliant ? "Compliant" : "Non-Compliant"}
          </span>
          <span className="text-sm font-bold">{score}%</span>
        </div>
      </div>
      <div className="space-y-1.5">
        {results.map(r => (
          <div key={r.id} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
            <span>{statusIcon(r.status)}</span>
            <span className="flex-1 text-sm">{r.label}</span>
            {r.required && <span className="text-[10px] text-gray-400">Required</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
