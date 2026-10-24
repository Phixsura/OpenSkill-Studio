"use client";

interface ValError { field: string; error: string; }
interface PayloadValCardProps { valid: boolean; errors: ValError[];
  errorCount: number; fieldsChecked: number; }

export function PayloadValCard({ valid, errors, errorCount, fieldsChecked }: PayloadValCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${valid ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">{valid ? "✅" : "❌"} Payload Validation</h3>
        <span className="text-xs text-gray-400">{fieldsChecked} fields · {errorCount} errors</span>
      </div>
      {errors.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="flex gap-2 px-4 py-1.5 text-xs">
              <span className="text-red-500">●</span>
              <span className="font-mono">{e.field}</span>
              <span className="text-gray-400">{e.error.replaceAll("_", " ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
