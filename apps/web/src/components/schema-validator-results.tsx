"use client";

interface SchemaError { path: string; error: string; message: string; }
interface SchemaValidatorResultsProps { valid: boolean; errors: SchemaError[]; errorCount: number; }

export function SchemaValidatorResults({ valid, errors, errorCount }: SchemaValidatorResultsProps) {
  return (
    <div className={`rounded-xl border p-4 ${valid ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">{valid ? "✅" : "❌"}</span>
        <span className="text-sm font-medium">{valid ? "Valid" : `${errorCount} validation errors`}</span>
      </div>
      {errors.length > 0 && (
        <div className="space-y-1">
          {errors.map((e, i) => (
            <div key={i} className="flex gap-2 text-xs">
              <span className="font-mono text-red-500 shrink-0">{e.path}</span>
              <span className="text-gray-500">{e.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
