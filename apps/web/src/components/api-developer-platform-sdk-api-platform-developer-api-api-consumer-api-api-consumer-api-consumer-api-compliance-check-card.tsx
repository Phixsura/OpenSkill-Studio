"use client";

interface Result { ruleId: string; name: string; passed: boolean; severity: string; }
interface Props { results: Result[]; score: number; passed: number; failed: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiComplianceCheckCard({ results, score, passed, failed, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Compliance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-lg font-bold ${score >= 80 ? "text-green-600" : score >= 50 ? "text-amber-600" : "text-red-600"}`}>{score}%</span>
      </div>
      <div className="mb-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{passed}</div><div className="text-[10px] text-gray-400">Passed</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{failed}</div><div className="text-[10px] text-gray-400">Failed</div></div>
      </div>
      {results.length > 0 && (
        <div className="space-y-1">
          {results.map((r) => (
            <div key={r.ruleId} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <span className="text-gray-700 dark:text-gray-300">{r.name}</span>
              <span className={r.passed ? "text-green-500" : "text-red-500"}>{r.passed ? "✓" : "✗"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
