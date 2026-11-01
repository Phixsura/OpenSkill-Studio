"use client";

interface RunInfo { run_id: string; consumer_id: string; status: string; pass_count: number; fail_count: number; total_tests: number; }
interface Props { runs: RunInfo[]; appName: string; }

const statusIcon: Record<string, string> = { queued: "⏳", running: "⚙️", passed: "✅", failed: "❌" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiTestSuiteCard({ runs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Test Suites</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {runs.length} runs</p>
      </div>
      {runs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No test runs</p>
      ) : (
        <div className="space-y-1">
          {runs.map((r) => (
            <div key={r.run_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{statusIcon[r.status] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.consumer_id}</span>
              </div>
              <span className="text-gray-400">{r.pass_count}✓ {r.fail_count}✗ / {r.total_tests}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
