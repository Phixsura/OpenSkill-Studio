"use client";

interface TestResult { name: string; passed: boolean; duration_ms: number; }
interface SandboxTestRunnerProps { results: TestResult[]; passRate: number; isRunning?: boolean; }

export function SandboxTestRunner({ results, passRate, isRunning }: SandboxTestRunnerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Test Results</h3>
        {isRunning ? (
          <span className="text-sm text-blue-600">⏳ Running...</span>
        ) : (
          <span className={`text-sm font-medium ${passRate === 100 ? "text-green-600" : "text-red-600"}`}>
            {passRate}% passed
          </span>
        )}
      </div>
      <ul className="mt-3 space-y-1">
        {results.map(r => (
          <li key={r.name} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <span>{r.passed ? "✅" : "❌"}</span>
              <span className={r.passed ? "" : "text-red-600 font-medium"}>{r.name}</span>
            </span>
            <span className="text-xs text-gray-400">{r.duration_ms}ms</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
