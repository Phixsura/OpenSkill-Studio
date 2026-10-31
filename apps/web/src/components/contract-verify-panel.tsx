"use client";
interface ContractResult { producer: string; consumer: string; compatible: boolean; missingFields: string[]; }
interface ContractVerifyPanelProps { results: ContractResult[]; allCompatible: boolean; compatible: number; total: number; }
export function ContractVerifyPanel({ results, allCompatible, compatible, total }: ContractVerifyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🤝 Contract Verification</h3>
        <span className={`text-xs font-bold ${allCompatible ? "text-green-600" : "text-red-500"}`}>
          {compatible}/{total} compatible
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map((r, i) => (
          <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{r.producer} → {r.consumer}</span>
            <span className={r.compatible ? "text-green-600" : "text-red-500"}>
              {r.compatible ? "✅" : `❌ missing: ${r.missingFields.join(", ")}`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
