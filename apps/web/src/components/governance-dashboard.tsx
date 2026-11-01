"use client";

interface GovResult { policy: string; description: string; severity: string; passed: boolean; }
interface GovernanceDashboardProps { results: GovResult[]; score: number;
  violations: number; criticalViolations: number; compliant: boolean; }

const SEV_COLORS: Record<string, string> = {
  critical: "text-red-600", high: "text-orange-600", medium: "text-yellow-600",
};

export function GovernanceDashboard({ results, score, violations, criticalViolations, compliant }: GovernanceDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📏 Governance</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{score}%</span>
          <span className={compliant ? "text-green-600" : "text-red-500"}>
            {compliant ? "✅ Compliant" : `⚠ ${violations} violations`}
          </span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.policy} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{r.passed ? "✅" : "❌"}</span>
              <span>{r.description}</span>
            </div>
            <span className={SEV_COLORS[r.severity] ?? "text-gray-400"}>{r.severity}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
