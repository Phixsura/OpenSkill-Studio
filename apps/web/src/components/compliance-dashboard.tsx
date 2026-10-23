"use client";

interface ComplianceCheck { check: string; pass: boolean; label: string; }
interface ComplianceDashboardProps { framework: string; region: string;
  checks: ComplianceCheck[]; score: number; compliant: boolean; passed: number; failed: number; }

export function ComplianceDashboard({ framework, region, checks, score, compliant, passed, failed }: ComplianceDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">{framework} Compliance</h3>
          <p className="text-xs text-gray-400">{region}</p>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${compliant ? "text-green-600" : "text-red-600"}`}>{score}%</span>
          <p className="text-xs text-gray-400">{compliant ? "✓ Compliant" : "✗ Non-compliant"}</p>
        </div>
      </div>
      <div className="flex gap-2 text-xs">
        <span className="text-green-600">{passed} passed</span>
        <span className="text-red-600">{failed} failed</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {checks.map(c => (
          <div key={c.check} className="flex items-center justify-between px-4 py-2.5">
            <span className="text-sm">{c.label}</span>
            <span className={c.pass ? "text-green-600" : "text-red-600"}>{c.pass ? "✓" : "✗"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
