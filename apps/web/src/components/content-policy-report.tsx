"use client";

interface Violation { rule: string; severity: string; detail: string; }
interface ContentPolicyReportProps { passed: boolean; violations: Violation[]; onFix: (rule: string) => void; }

export function ContentPolicyReport({ passed, violations, onFix }: ContentPolicyReportProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className={`h-3 w-3 rounded-full ${passed ? "bg-green-500" : "bg-red-500"}`} />
        <h2 className="text-lg font-semibold">Content Policy Check</h2>
        <span className={`ml-auto rounded-full px-2.5 py-0.5 text-xs font-medium ${passed ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {passed ? "Passed" : "Failed"}
        </span>
      </div>
      {violations.length === 0 ? (
        <p className="text-sm text-gray-400">No violations found ✓</p>
      ) : (
        <div className="space-y-2">
          {violations.map((v, i) => (
            <div key={i} className={`flex items-start justify-between rounded-lg border p-3 ${v.severity === "critical" ? "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10" : "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/10"}`}>
              <div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold uppercase ${v.severity === "critical" ? "text-red-600" : "text-yellow-600"}`}>{v.severity}</span>
                  <span className="font-mono text-xs text-gray-400">{v.rule}</span>
                </div>
                <p className="mt-0.5 text-sm">{v.detail}</p>
              </div>
              <button onClick={() => onFix(v.rule)} className="rounded border px-2 py-1 text-xs">Fix</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
