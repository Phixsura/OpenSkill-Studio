"use client";

interface TestResult { name: string; method: string; path: string;
  expectedStatus: number; actualStatus: number; passed: boolean; durationMs: number; }
interface ApiTestResultsProps { results: TestResult[]; passed: number; failed: number;
  passRate: number; totalMs: number; allPassed: boolean; }

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600",
};

export function ApiTestResults({ results, passed, failed, passRate, totalMs, allPassed }: ApiTestResultsProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">🧪 API Tests</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${allPassed ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-xs text-gray-400">{passRate}% · {totalMs}ms</span>
        </div>
      </div>
      <div className="flex gap-3 text-xs">
        <span className="text-green-600">✓ {passed} passed</span>
        {failed > 0 && <span className="text-red-600">✗ {failed} failed</span>}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {results.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span className={r.passed ? "text-green-600" : "text-red-600"}>{r.passed ? "✓" : "✗"}</span>
              <span className={`text-xs font-mono ${methodColors[r.method] ?? ""}`}>{r.method}</span>
              <span className="text-sm">{r.name}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              {!r.passed && <span className="text-red-500">{r.actualStatus} ≠ {r.expectedStatus}</span>}
              <span>{r.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
