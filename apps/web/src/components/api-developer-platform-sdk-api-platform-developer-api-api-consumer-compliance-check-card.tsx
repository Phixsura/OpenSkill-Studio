"use client";

interface CheckResult { consumer_id: string; compliant: number; non_compliant: number; total_rules: number; overall: string; }
interface Props { results: CheckResult[]; nonCompliantCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerComplianceCheckCard({ results, nonCompliantCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Compliance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {results.length} consumers</p>
        </div>
        {nonCompliantCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {nonCompliantCount} non-compliant</span>}
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No compliance data</p>
      ) : (
        <div className="space-y-1">
          {results.map((r) => (
            <div key={r.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.consumer_id}</span>
              <span className={r.overall === "compliant" ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{r.compliant}/{r.total_rules} ✓</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
