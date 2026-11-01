"use client";

interface Check { name: string; passed: boolean; message: string; }
interface TestSuiteResultsPanelProps { checks: Check[]; score: number; readyToPublish: boolean; onPublish: () => void; }

export function TestSuiteResultsPanel({ checks, score, readyToPublish, onPublish }: TestSuiteResultsPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Pre-Publish Tests</h2>
        <span className={`text-lg font-bold ${score === 100 ? "text-green-600" : score >= 50 ? "text-yellow-600" : "text-red-600"}`}>
          {score}%
        </span>
      </div>
      <div className="space-y-1.5">
        {checks.map(c => (
          <div key={c.name} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
            <span className={c.passed ? "text-green-500" : "text-red-500"}>{c.passed ? "✓" : "✗"}</span>
            <span className={`flex-1 text-sm ${c.passed ? "" : "text-red-600 dark:text-red-400"}`}>{c.message}</span>
          </div>
        ))}
      </div>
      <button onClick={onPublish} disabled={!readyToPublish}
        className="w-full rounded-lg bg-green-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        {readyToPublish ? "Publish App" : "Fix issues to publish"}
      </button>
    </div>
  );
}
