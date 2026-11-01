"use client";

interface SandboxDebugPanelProps { executionId: string; functionName: string; durationMs: number; success: boolean;
  logCount: number; error: string | null; envCount: number; }

export function SandboxDebugPanel({ executionId, functionName, durationMs, success, logCount, error, envCount }: SandboxDebugPanelProps) {
  return (
    <div className={`rounded-lg border p-4 ${success ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-semibold">🔧 Debug: <code className="text-sm">{functionName}</code></h4>
        <span className={success ? "text-green-600" : "text-red-600"}>{success ? "✅ OK" : "❌ Failed"}</span>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-xs text-gray-500">
        <div><p className="font-bold text-sm">{durationMs}ms</p>Duration</div>
        <div><p className="font-bold text-sm">{logCount}</p>Logs</div>
        <div><p className="font-bold text-sm">{envCount}</p>Env Vars</div>
        <div><p className="font-mono text-xs">{executionId.slice(0, 8)}</p>ID</div>
      </div>
      {error && <p className="mt-2 rounded bg-red-50 p-2 text-sm text-red-700 dark:bg-red-900/20">{error}</p>}
    </div>
  );
}
