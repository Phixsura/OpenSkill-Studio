"use client";

interface ExecutionResultCardProps {
  success: boolean;
  durationMs: number;
  memoryMb: number;
  logCount: number;
  error?: string | null;
  output?: Record<string, unknown> | null;
}

export function ExecutionResultCard({ success, durationMs, memoryMb, logCount, error, output }: ExecutionResultCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${success ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="mb-2 flex items-center justify-between">
        <span className="font-semibold">{success ? "✅ Success" : "❌ Failed"}</span>
        <span className="text-xs text-gray-500">{durationMs}ms · {memoryMb}MB · {logCount} logs</span>
      </div>
      {error && <p className="rounded bg-red-50 p-2 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-300">{error}</p>}
      {output && (
        <pre className="mt-2 max-h-40 overflow-auto rounded bg-gray-100 p-2 text-xs dark:bg-gray-800">
          {JSON.stringify(output, null, 2)}
        </pre>
      )}
    </div>
  );
}
