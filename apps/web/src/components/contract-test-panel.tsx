"use client";
interface TestResult { name: string; valid: boolean; errors: number; }
interface ContractTestPanelProps { results: TestResult[]; passed: number; failed: number; }
export function ContractTestPanel({ results, passed, failed }: ContractTestPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Contract Tests</h3>
        <span className={`text-xs font-bold ${failed > 0 ? "text-red-500" : "text-green-600"}`}>
          {passed}/{passed + failed} passed
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.name}</span>
            <span className={r.valid ? "text-green-600" : "text-red-500"}>
              {r.valid ? "✅" : `❌ ${r.errors} errors`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
