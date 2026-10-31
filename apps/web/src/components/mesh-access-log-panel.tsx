"use client";
interface AccessEntry { source: string; destination: string; method: string; path: string; status: number; durationMs: number; }
interface MeshAccessLogPanelProps { entries: AccessEntry[]; total: number; errors: number; }
export function MeshAccessLogPanel({ entries, total, errors }: MeshAccessLogPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Mesh Access Log</h3>
        <span className="text-xs text-gray-400">{total} entries · {errors} errors</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1 text-[11px]">
            <span className="font-mono">{e.source}→{e.destination} {e.method} {e.path}</span>
            <div className="flex gap-2">
              <span className={e.status >= 500 ? "text-red-500" : "text-green-600"}>{e.status}</span>
              <span className="text-gray-400">{e.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
