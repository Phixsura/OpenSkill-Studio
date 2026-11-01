"use client";

interface TestResult { url: string; method: string; pass: boolean; actualStatus: number; responseMs: number; }
interface EndpointTesterProps { results: TestResult[]; passed: number; failed: number; allPass: boolean; avgResponseMs: number; }

export function EndpointTester({ results, passed, failed, allPass, avgResponseMs }: EndpointTesterProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Endpoint Tests</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${allPass ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-xs text-gray-400">{passed}✓ {failed}✗ · avg {avgResponseMs}ms</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {results.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span className={r.pass ? "text-green-600" : "text-red-600"}>{r.pass ? "✓" : "✗"}</span>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono dark:bg-gray-800">{r.method}</span>
              <span className="text-sm font-mono truncate max-w-[300px]">{r.url}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span className="font-mono">{r.actualStatus}</span>
              <span>{r.responseMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
