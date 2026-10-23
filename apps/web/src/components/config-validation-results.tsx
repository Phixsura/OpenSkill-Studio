"use client";

interface Issue { field: string; message: string; }
interface ConfigValidationResultsProps { valid: boolean; errors: Issue[]; warnings: Issue[]; fieldsPresent: number; fieldsRequired: number; }

export function ConfigValidationResults({ valid, errors, warnings, fieldsPresent, fieldsRequired }: ConfigValidationResultsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Config Validation</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${valid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {valid ? "✅ Valid" : "❌ Invalid"}
        </span>
      </div>
      <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
        <p className="text-lg font-bold">{fieldsPresent}/{fieldsRequired}</p>
        <p className="text-xs text-gray-400">Required fields</p>
      </div>
      {errors.length > 0 && (
        <div className="space-y-1">
          <h3 className="text-sm font-medium text-red-600">Errors</h3>
          {errors.map((e, i) => (
            <div key={i} className="flex items-center gap-2 rounded border border-red-200 px-3 py-1.5 text-sm dark:border-red-800">
              <span className="text-red-500">✗</span>
              <code className="text-xs text-gray-400">{e.field}</code>
              <span>{e.message}</span>
            </div>
          ))}
        </div>
      )}
      {warnings.length > 0 && (
        <div className="space-y-1">
          <h3 className="text-sm font-medium text-yellow-600">Warnings</h3>
          {warnings.map((w, i) => (
            <div key={i} className="flex items-center gap-2 rounded border border-yellow-200 px-3 py-1.5 text-sm dark:border-yellow-800">
              <span className="text-yellow-500">⚠</span>
              <span>{w.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
