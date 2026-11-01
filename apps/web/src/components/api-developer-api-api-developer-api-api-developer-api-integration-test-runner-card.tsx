"use client";

interface RunInfo { run_id: string; suite_name: string; total: number; passed: number; failed: number; pass_rate: number; all_passed: boolean; }
interface Props { runs: RunInfo[]; failingCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiIntegrationTestRunnerCard({ runs, failingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Integration Tests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {failingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{failingCount} failing</span>}
      </div>
      {runs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No test runs</p>
      ) : (
        <div className="space-y-1.5">
          {runs.map((r) => (
            <div key={r.run_id} className={`flex items-center justify-between rounded-lg px-3 py-1.5 ${r.all_passed ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
              <span className="text-[11px] text-gray-700 dark:text-gray-300">{r.suite_name}</span>
              <div className="flex gap-2 text-[10px]">
                <span className="text-green-600">{r.passed}✓</span>
                {r.failed > 0 && <span className="text-red-500">{r.failed}✗</span>}
                <span className="text-gray-400">{r.pass_rate}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
