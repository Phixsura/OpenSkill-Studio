"use client";

interface ContractResult { endpoint: string; valid: boolean; errors: string[]; }
interface ContractTestResultsProps { results: ContractResult[]; passRate: number; }

export function ContractTestResults({ results, passRate }: ContractTestResultsProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Contract Tests</h3>
        <span className={`text-sm font-bold ${passRate === 100 ? "text-green-600" : "text-red-600"}`}>{passRate}%</span>
      </div>
      <ul className="mt-3 space-y-2">
        {results.map((r, i) => (
          <li key={i} className="rounded border p-2 dark:border-gray-700">
            <div className="flex items-center justify-between text-sm">
              <code className="text-xs">{r.endpoint}</code>
              <span>{r.valid ? "✅" : "❌"}</span>
            </div>
            {r.errors.length > 0 && (
              <ul className="mt-1 text-xs text-red-600">
                {r.errors.map((e, j) => <li key={j}>• {e}</li>)}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
