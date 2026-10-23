"use client";

interface ContractResult { contractName: string; valid: boolean; errorCount: number; fieldsChecked: number; }
interface ContractTestResultsProps { results: ContractResult[]; passRate: number;
  passed: number; failed: number; }

export function ContractTestResults({ results, passRate, passed, failed }: ContractTestResultsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Contract Tests</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{passed} passed</span>
          {failed > 0 && <span className="text-red-500">{failed} failed</span>}
          <span className="text-gray-400">{passRate}%</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.contractName} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{r.valid ? "✅" : "❌"}</span>
              <span className="text-sm font-mono">{r.contractName}</span>
            </div>
            <span className="text-xs text-gray-400">{r.fieldsChecked} fields · {r.errorCount} errors</span>
          </div>
        ))}
      </div>
    </div>
  );
}
