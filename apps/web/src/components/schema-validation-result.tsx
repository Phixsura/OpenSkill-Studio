"use client";

interface ValidationError { field: string; error: string; }
interface SchemaValidationResultProps { valid: boolean; errors: ValidationError[]; onFix: (field: string) => void; }

export function SchemaValidationResult({ valid, errors, onFix }: SchemaValidationResultProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Schema Validation</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${valid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {valid ? "✅ Valid" : `❌ ${errors.length} errors`}
        </span>
      </div>
      {errors.length > 0 && (
        <div className="space-y-1.5">
          {errors.map((e, i) => (
            <div key={i} className="flex items-center justify-between rounded border border-red-200 px-3 py-2 dark:border-red-800">
              <div>
                <code className="text-xs font-bold text-red-600">{e.field}</code>
                <p className="text-xs text-gray-400">{e.error}</p>
              </div>
              <button onClick={() => onFix(e.field)} className="text-xs text-blue-500">Fix</button>
            </div>
          ))}
        </div>
      )}
      {valid && <p className="text-center text-sm text-green-600">All fields pass validation ✓</p>}
    </div>
  );
}
