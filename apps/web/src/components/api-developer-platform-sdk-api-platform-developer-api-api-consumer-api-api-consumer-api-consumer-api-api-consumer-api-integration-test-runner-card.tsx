"use client";

interface Run { id: string; passed: number; failed: number; total: number; runAt: string; }
interface Props { runs: Run[]; suiteCount: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiIntegrationTestRunnerCard({ runs, suiteCount, consumerId, appName }: Props) {
  const latest = runs[runs.length - 1];
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Integration Tests</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {suiteCount} suites</p>
      </div>
      {latest && (
        <div className={`mb-3 rounded-lg p-2 text-center text-[11px] ${latest.failed === 0 ? "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400" : "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400"}`}>
          {latest.failed === 0 ? "✅ All tests passed" : `❌ ${latest.failed} failed`} — {latest.passed}/{latest.total} passed
        </div>
      )}
      {runs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No test runs</p>
      ) : (
        <div className="space-y-0.5">
          {runs.slice(-5).reverse().map((r) => (
            <div key={r.id} className="flex justify-between text-[10px] text-gray-500">
              <span>{r.runAt}</span>
              <span className={r.failed === 0 ? "text-green-500" : "text-red-500"}>{r.passed}/{r.total}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
