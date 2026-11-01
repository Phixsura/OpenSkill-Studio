"use client";

interface ValidationError { field: string; error: string; }
interface ResponseValidatorProps { valid: boolean; errors: ValidationError[];
  checkedFields: number; passedFields: number; }

export function ResponseValidator({ valid, errors, checkedFields, passedFields }: ResponseValidatorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Response Validation</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${valid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {valid ? `✓ ${passedFields}/${checkedFields} passed` : `✗ ${errors.length} errors`}
        </span>
      </div>
      {errors.length > 0 && (
        <div className="space-y-1">
          {errors.map((e, i) => (
            <div key={i} className="flex items-center gap-2 text-xs">
              <span className="text-red-500">✗</span>
              <code className="font-mono">{e.field}</code>
              <span className="text-gray-400">— {e.error}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
