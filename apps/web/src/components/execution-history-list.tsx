"use client";

interface Execution { functionName: string; success: boolean; durationMs: number; trigger: string; timestamp: string; error?: string | null; }

interface ExecutionHistoryListProps { executions: Execution[]; }

export function ExecutionHistoryList({ executions }: ExecutionHistoryListProps) {
  if (executions.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No executions</p>;
  return (
    <div className="space-y-1">
      {executions.map((ex, i) => (
        <div key={i} className="flex items-center gap-2 rounded border border-gray-200 p-2 text-sm dark:border-gray-700">
          <span>{ex.success ? "✅" : "❌"}</span>
          <span className="font-mono text-xs">{ex.functionName}</span>
          <span className="text-xs text-gray-500">{ex.durationMs}ms</span>
          <span className="ml-auto text-xs text-gray-400">{ex.timestamp}</span>
        </div>
      ))}
    </div>
  );
}
