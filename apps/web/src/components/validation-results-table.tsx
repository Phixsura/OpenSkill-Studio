"use client";

interface ValidationResultsTableProps { total: number; valid: number;
  invalid: number; passRate: number;
  errors: { field: string; rule: string; message: string }[]; }

export function ValidationResultsTable({ total, valid, invalid, passRate, errors }: ValidationResultsTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✅ Data Validation</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{valid} valid</span>
          {invalid > 0 && <span className="text-red-500">{invalid} invalid</span>}
          <span className="text-gray-400">{passRate}%</span>
        </div>
      </div>
      {errors.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs">
              <span className="text-red-500">●</span>
              <span className="font-mono font-medium">{e.field}</span>
              <span className="text-gray-400">{e.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
