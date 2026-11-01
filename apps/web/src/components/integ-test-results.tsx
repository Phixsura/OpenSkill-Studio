"use client";

interface TestResult { name: string; status: string; durationMs: number; error: string; }
interface IntegTestResultsProps { suite: string; results: TestResult[];
  passed: number; failed: number; passRate: number; durationMs: number; }

const STATUS_ICON: Record<string, string> = { passed: "✅", failed: "❌", skipped: "⏭️" };

export function IntegTestResults({ suite, results, passed, failed, passRate, durationMs }: IntegTestResultsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">🧪 {suite}</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{passed} passed</span>
          {failed > 0 && <span className="text-red-500">{failed} failed</span>}
          <span className="text-gray-400">{passRate}% · {durationMs}ms</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.name} className="px-4 py-2 text-xs">
            <div className="flex items-center justify-between">
              <span>{STATUS_ICON[r.status] ?? "⚪"} {r.name}</span>
              <span className="text-gray-400">{r.durationMs}ms</span>
            </div>
            {r.error && <div className="text-red-500 mt-0.5 font-mono">{r.error}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
