"use client";

interface ExecutionContext {
  id: string;
  functionName: string;
  status: "pending" | "running" | "completed" | "failed" | "timeout" | "cancelled";
  durationMs: number;
  memoryMb: number;
  cpuMs: number;
  error?: string;
  inputKeys: string[];
  outputKeys: string[];
}

interface ExecStats {
  total: number;
  completed: number;
  failed: number;
  timeouts: number;
  avgDurationMs: number;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  pending: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏳" },
  running: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "▶" },
  completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  timeout: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏰" },
  cancelled: { color: "bg-gray-200 text-gray-500 dark:bg-gray-800", icon: "⊘" },
};

export function ExecutionContextPanel({
  contexts,
  stats,
  onCancel,
}: {
  contexts: ExecutionContext[];
  stats: ExecStats;
  onCancel?: (id: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⚡ Execution Contexts</h2>

      <div className="grid grid-cols-4 gap-2 text-center">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Total</span>
          <span className="font-bold">{stats.total}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Success</span>
          <span className="font-bold text-green-600">{stats.completed}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Failed</span>
          <span className="font-bold text-red-600">{stats.failed}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Avg Time</span>
          <span className="font-bold">{stats.avgDurationMs}ms</span>
        </div>
      </div>

      <div className="space-y-2">
        {contexts.map((ctx) => {
          const cfg = statusConfig[ctx.status];
          return (
            <div key={ctx.id} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <code className="text-sm font-semibold">{ctx.functionName}</code>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{ctx.status}</span>
                </div>
                <div className="flex items-center gap-2">
                  {ctx.durationMs > 0 && <span className="text-xs text-gray-400">{ctx.durationMs}ms</span>}
                  {(ctx.status === "pending" || ctx.status === "running") && (
                    <button onClick={() => onCancel?.(ctx.id)}
                      className="text-xs bg-red-500 text-white px-2 py-0.5 rounded">Cancel</button>
                  )}
                </div>
              </div>
              {(ctx.memoryMb > 0 || ctx.cpuMs > 0) && (
                <div className="text-xs text-gray-500">
                  {ctx.memoryMb > 0 && <span className="mr-3">RAM: {ctx.memoryMb}MB</span>}
                  {ctx.cpuMs > 0 && <span>CPU: {ctx.cpuMs}ms</span>}
                </div>
              )}
              {ctx.error && <div className="text-xs text-red-500 mt-1">{ctx.error}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
