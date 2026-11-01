"use client";

interface SuiteResult { name: string; passed: number; failed: number; skipped: number; total: number; duration_ms: number; status: string; }
interface TestSummary { passed: number; failed: number; skipped: number; total: number; }
interface TestPipelineResultsProps { suites: SuiteResult[]; summary: TestSummary;
  allPassed: boolean; publishable: boolean; onPublish: () => void; }

export function TestPipelineResults({ suites, summary, allPassed, publishable, onPublish }: TestPipelineResultsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Test Results</h2>
        <span className={`rounded-full px-3 py-1 text-sm font-bold ${allPassed ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {allPassed ? "✅ All Passed" : "❌ Failures"}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded bg-green-50 p-2 dark:bg-green-900/10">
          <p className="text-lg font-bold text-green-600">{summary.passed}</p>
          <p className="text-xs text-gray-400">Passed</p>
        </div>
        <div className="rounded bg-red-50 p-2 dark:bg-red-900/10">
          <p className="text-lg font-bold text-red-600">{summary.failed}</p>
          <p className="text-xs text-gray-400">Failed</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-400">{summary.skipped}</p>
          <p className="text-xs text-gray-400">Skipped</p>
        </div>
      </div>
      <div className="space-y-2">
        {suites.map(s => (
          <div key={s.name} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{s.status === "passed" ? "✅" : "❌"}</span>
              <span className="text-sm font-medium">{s.name}</span>
            </div>
            <span className="text-xs text-gray-400">{s.passed}/{s.total} · {s.duration_ms}ms</span>
          </div>
        ))}
      </div>
      <button onClick={onPublish} disabled={!publishable}
        className="w-full rounded bg-green-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        {publishable ? "Publish App" : "Fix tests to publish"}
      </button>
    </div>
  );
}
