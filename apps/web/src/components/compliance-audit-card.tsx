"use client";

interface ComplianceRule { id: string; label: string; category: string; severity: string; passed: boolean; }
interface ComplianceAuditCardProps { rules: ComplianceRule[]; score: number; compliant: boolean; criticalFailures: number; }

const SEV_COLORS: Record<string, string> = { critical: "text-red-600", high: "text-orange-600", medium: "text-yellow-600" };

export function ComplianceAuditCard({ rules, score, compliant, criticalFailures }: ComplianceAuditCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${compliant ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Compliance Audit</h3>
        <div className="text-right">
          <span className={`text-2xl font-bold ${score >= 80 ? "text-green-600" : score >= 50 ? "text-yellow-600" : "text-red-600"}`}>{score}%</span>
          {criticalFailures > 0 && <p className="text-xs text-red-600">{criticalFailures} critical</p>}
        </div>
      </div>
      <ul className="mt-3 space-y-1">
        {rules.map(r => (
          <li key={r.id} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-1">
              <span>{r.passed ? "✅" : "❌"}</span>
              <span className={r.passed ? "" : "font-medium"}>{r.label}</span>
            </span>
            {!r.passed && <span className={`text-xs ${SEV_COLORS[r.severity] || ""}`}>{r.severity}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
