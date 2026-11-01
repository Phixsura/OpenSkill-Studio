"use client";

interface FailureInfo { endpoint: string; field: string; rule: string; count: number; }
interface Props { failures: FailureInfo[]; totalFailures: number; ruleBreakdown: Record<string, number>; appName: string; }

const ruleColor: Record<string, string> = { required: "text-red-600", type: "text-orange-600", format: "text-yellow-600", range: "text-blue-600", pattern: "text-purple-600" };

export default function APIDeveloperAPIRequestValidationReportCard({ failures, totalFailures, ruleBreakdown, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Validation Report</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-red-500">{totalFailures.toLocaleString()}</span>
      </div>
      <div className="mb-3 flex flex-wrap gap-1.5">
        {Object.entries(ruleBreakdown).map(([rule, count]) => (
          <span key={rule} className={`text-[10px] font-medium ${ruleColor[rule] ?? "text-gray-500"}`}>{rule}: {count}</span>
        ))}
      </div>
      {failures.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No validation failures</p>
      ) : (
        <div className="space-y-1">
          {failures.map((f, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{f.endpoint} → {f.field}</span>
              <span className="text-gray-400">{f.rule} ×{f.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
