"use client";

interface TestResult { name: string; valid: boolean; errors: { field: string; error?: string }[]; }
interface ContractTestResultsProps { total: number; passed: number; failed: number;
  passRate: number; results: TestResult[]; allPassed: boolean; }

export function ContractTestResults({ total, passed, failed, passRate, results, allPassed }: ContractTestResultsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 Contract Tests</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${allPassed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {passRate}% · {passed}/{total} passed
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.name} className="px-4 py-3">
            <div className="flex items-center gap-2">
              <span>{r.valid ? "✅" : "❌"}</span>
              <span className="text-sm font-medium">{r.name}</span>
            </div>
            {r.errors.length > 0 && (
              <div className="ml-7 mt-1 space-y-0.5">
                {r.errors.map((e, i) => (
                  <p key={i} className="text-xs text-red-500">{e.field}: {e.error || "mismatch"}</p>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
