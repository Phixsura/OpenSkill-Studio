"use client";

interface CapturedRequest { method: string; path: string; status_code: number; duration_ms: number; captured_at: string; }
interface RequestInspectorPanelProps { requests: CapturedRequest[]; }

const STATUS_COLORS: Record<string, string> = { "2": "text-green-600", "3": "text-blue-600", "4": "text-yellow-600", "5": "text-red-600" };
const METHOD_COLORS: Record<string, string> = { GET: "bg-green-100 text-green-700", POST: "bg-blue-100 text-blue-700", PUT: "bg-yellow-100 text-yellow-700", DELETE: "bg-red-100 text-red-700" };

export function RequestInspectorPanel({ requests }: RequestInspectorPanelProps) {
  if (requests.length === 0) return <p className="text-sm text-gray-400">No requests captured.</p>;
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700"><h3 className="font-semibold text-sm">Request Inspector</h3></div>
      <div className="max-h-64 overflow-y-auto">
        {requests.map((r, i) => (
          <div key={i} className="flex items-center gap-3 border-b px-3 py-2 text-xs dark:border-gray-700">
            <span className={`rounded px-1.5 py-0.5 font-mono ${METHOD_COLORS[r.method] || "bg-gray-100"}`}>{r.method}</span>
            <span className="flex-1 truncate font-mono">{r.path}</span>
            <span className={STATUS_COLORS[String(r.status_code)[0]] || ""}>{r.status_code}</span>
            <span className="text-gray-400">{r.duration_ms}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
