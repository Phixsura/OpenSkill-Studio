"use client";

interface CheckResult { check: string; passed: boolean; }
interface PolicyResult { policy: string; checks: CheckResult[]; passed: number;
  total: number; compliant: boolean; compliancePct: number; }
interface ComplianceDashboardProps { policies: Record<string, PolicyResult>; overall: boolean; }

export function ComplianceDashboard({ policies, overall }: ComplianceDashboardProps) {
  const entries = Object.entries(policies);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏛️ Compliance</h3>
        <span className={`text-xs font-medium ${overall ? "text-green-600" : "text-yellow-600"}`}>
          {overall ? "✅ All Compliant" : "⚠ Action Required"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(([id, p]) => (
          <div key={id} className="px-4 py-3">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm font-medium">{p.policy}</span>
              <span className={`text-xs ${p.compliant ? "text-green-600" : "text-yellow-600"}`}>
                {p.passed}/{p.total} ({p.compliancePct}%)
              </span>
            </div>
            <div className="flex gap-1">
              {p.checks.map(c => (
                <span key={c.check} title={c.check.replaceAll("_", " ")}
                  className={`w-4 h-4 rounded text-center text-[8px] leading-4 ${c.passed ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700"}`}>
                  {c.passed ? "✓" : ""}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
