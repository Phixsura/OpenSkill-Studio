"use client";

interface ValidationError { field: string; error: string; }
interface RequestValidatorDebugProps { valid: boolean; errors: ValidationError[];
  method: string; path: string; }

export function RequestValidatorDebug({ valid, errors, method, path }: RequestValidatorDebugProps) {
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`rounded px-1.5 py-0.5 font-mono text-xs font-bold ${method === "GET" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}`}>{method}</span>
          <span className="font-mono text-sm">{path}</span>
        </div>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${valid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {valid ? "✅ Valid" : `❌ ${errors.length} errors`}
        </span>
      </div>
      {errors.length > 0 && (
        <div className="space-y-1">
          {errors.map((e, i) => (
            <div key={i} className="flex items-center gap-2 rounded border border-red-200 px-3 py-1.5 text-xs dark:border-red-800">
              <code className="font-bold text-red-600">{e.field}</code>
              <span className="text-gray-400">{e.error}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
