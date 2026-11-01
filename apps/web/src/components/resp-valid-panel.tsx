"use client";
interface RespValidError { field: string; error: string; }
interface RespValidPanelProps { valid: boolean; errors: RespValidError[]; fieldsChecked: number; validityPct: number; }
export function RespValidPanel({ valid, errors, fieldsChecked, validityPct }: RespValidPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">✅ Response Validator</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {validityPct}% valid · {fieldsChecked} fields
        </span>
      </div>
      {errors.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{e.field}</span>: {e.error}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
