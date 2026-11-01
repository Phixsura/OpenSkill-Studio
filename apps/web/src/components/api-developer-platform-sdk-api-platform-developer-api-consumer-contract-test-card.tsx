"use client";

interface TestInfo { test_id: string; endpoint: string; method: string; last_result: string; }
interface Props { consumerId: string; tests: TestInfo[]; passRate: number; appName: string; }

const resultIcon: Record<string, string> = { passed: "✅", failed: "❌", skipped: "⏭️" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerContractTestCard({ consumerId, tests, passRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Contract Tests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-sm font-bold ${passRate >= 90 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{passRate}%</span>
      </div>
      {tests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No contract tests</p>
      ) : (
        <div className="space-y-1">
          {tests.map((t) => (
            <div key={t.test_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{resultIcon[t.last_result] ?? "⚪"}</span>
                <span className="font-mono text-gray-500">{t.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{t.endpoint}</span>
              </div>
              <span className="text-gray-400">{t.last_result}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
