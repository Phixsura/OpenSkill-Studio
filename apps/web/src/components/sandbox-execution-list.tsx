"use client";

interface Execution { id: string; functionName: string; success: boolean; durationMs: number; timestamp: string; }
interface SandboxExecutionListProps { executions: Execution[]; total: number; }

export function SandboxExecutionList({ executions, total }: SandboxExecutionListProps) {
  if (executions.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No executions</p>;
  return (
    <div>
      <p className="mb-2 text-xs text-gray-500">{total} total executions</p>
      <div className="space-y-1">{executions.map(e => (
        <div key={e.id} className="flex items-center gap-2 rounded border border-gray-200 p-2 text-sm dark:border-gray-700">
          <span>{e.success ? "✅" : "❌"}</span>
          <code className="text-xs">{e.functionName}</code>
          <span className="text-xs text-gray-400">{e.durationMs}ms</span>
          <span className="ml-auto text-xs text-gray-400">{e.timestamp}</span>
        </div>
      ))}</div>
    </div>
  );
}
