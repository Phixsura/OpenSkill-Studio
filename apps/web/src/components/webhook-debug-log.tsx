"use client";

interface DebugEntry { eventType: string; statusCode: number | null; durationMs: number | null; success: boolean; error: string | null; timestamp: string; }
interface WebhookDebugLogProps { entries: DebugEntry[]; }

export function WebhookDebugLog({ entries }: WebhookDebugLogProps) {
  if (entries.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No debug logs</p>;
  return (
    <div className="space-y-1 font-mono text-xs">
      {entries.map((e, i) => (
        <div key={i} className={`flex items-center gap-2 rounded p-1 ${e.success ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
          <span>{e.success ? "✅" : "❌"}</span>
          <span className="w-32 truncate">{e.eventType}</span>
          <span>{e.statusCode ?? "—"}</span>
          <span>{e.durationMs ?? 0}ms</span>
          <span className="flex-1 text-right text-gray-400">{e.timestamp}</span>
        </div>
      ))}
    </div>
  );
}
