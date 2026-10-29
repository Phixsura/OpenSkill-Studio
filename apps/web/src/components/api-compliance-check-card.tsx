"use client";

interface ComplianceRuleInfo {
  rule_id: string;
  name: string;
  category: string;
  passed: boolean | null;
}

interface APIComplianceCheckCardProps {
  rules: ComplianceRuleInfo[];
  score: number;
  appName: string;
}

export default function APIComplianceCheckCard({ rules, score, appName }: APIComplianceCheckCardProps) {
  const failing = rules.filter((r) => r.passed === false).length;
  const scoreColor = score >= 90 ? "text-green-600" : score >= 70 ? "text-yellow-600" : "text-red-500";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Compliance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${scoreColor}`}>{score}%</span>
          {failing > 0 && <p className="text-[10px] text-red-500">{failing} failing</p>}
        </div>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No compliance rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center gap-2 text-[11px]">
              <span className={r.passed === true ? "text-green-500" : r.passed === false ? "text-red-500" : "text-gray-300"}>
                {r.passed === true ? "✓" : r.passed === false ? "✗" : "○"}
              </span>
              <span className="text-gray-700 dark:text-gray-300">{r.name}</span>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{r.category}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
