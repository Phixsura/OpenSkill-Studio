"use client";

interface ValidationError { key: string; error: string; }
interface ValidationWarning { key: string; warning: string; }
interface ConfigValidationResultProps { valid: boolean; errors: ValidationError[];
  warnings: ValidationWarning[]; }

export function ConfigValidationResult({ valid, errors, warnings }: ConfigValidationResultProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${valid ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">{valid ? "✅ Config Valid" : "❌ Validation Failed"}</h3>
        <div className="flex gap-2 text-xs">
          {errors.length > 0 && <span className="text-red-600">{errors.length} errors</span>}
          {warnings.length > 0 && <span className="text-yellow-600">{warnings.length} warnings</span>}
        </div>
      </div>
      {errors.length > 0 && (
        <div className="border-b dark:border-gray-700">
          {errors.map((e, i) => (
            <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs">
              <span className="text-red-500">●</span>
              <span className="font-mono font-medium">{e.key}</span>
              <span className="text-gray-400">{e.error.replaceAll("_", " ")}</span>
            </div>
          ))}
        </div>
      )}
      {warnings.length > 0 && warnings.map((w, i) => (
        <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs">
          <span className="text-yellow-500">●</span>
          <span className="font-mono font-medium">{w.key}</span>
          <span className="text-gray-400">{w.warning.replaceAll("_", " ")}</span>
        </div>
      ))}
    </div>
  );
}
