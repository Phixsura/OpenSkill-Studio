"use client";

interface TestResult { name: string; passed: boolean; duration_ms: number; actual_status: number; }
interface TestSuiteRunnerCardProps { name: string; results: TestResult[]; passRate: number; totalMs: number; onRerun: () => void; }

export function TestSuiteRunnerCard({ name, results, passRate, totalMs, onRerun }: TestSuiteRunnerCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">{name}</h3>
          <p className="text-xs text-gray-400">{results.length} tests · {totalMs}ms</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-lg font-bold ${passRate === 100 ? "text-green-600" : "text-red-600"}`}>{passRate}%</span>
          <button onClick={onRerun} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">▶ Run</button>
        </div>
      </div>
      <ul className="mt-3 space-y-0.5">
        {results.map(r => (
          <li key={r.name} className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1">
              <span>{r.passed ? "✅" : "❌"}</span>
              <span className={r.passed ? "" : "text-red-600 font-medium"}>{r.name}</span>
            </span>
            <span className="text-gray-400">{r.duration_ms}ms · {r.actual_status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
