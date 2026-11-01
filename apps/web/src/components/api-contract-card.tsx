"use client";

interface ContractInfo {
  contract_id: string;
  method: string;
  path: string;
  request_field_count: number;
  response_field_count: number;
  violation_count: number;
}

interface APIContractCardProps {
  contracts: ContractInfo[];
  appName: string;
}

export default function APIContractCard({ contracts, appName }: APIContractCardProps) {
  const totalViolations = contracts.reduce((s, c) => s + c.violation_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📜 API Contracts
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{contracts.length} contracts</span>
          {totalViolations > 0 && (
            <p className="text-[10px] text-red-500">{totalViolations} violations</p>
          )}
        </div>
      </div>

      {contracts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API contracts</p>
      ) : (
        <div className="space-y-1.5">
          {contracts.map((c) => (
            <div
              key={c.contract_id}
              className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[10px] font-medium text-gray-600 dark:bg-gray-800">
                    {c.method}
                  </span>
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                    {c.path}
                  </span>
                </div>
                {c.violation_count > 0 && (
                  <span className="text-[10px] text-red-500">{c.violation_count}</span>
                )}
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">
                {c.request_field_count} req · {c.response_field_count} resp fields
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
