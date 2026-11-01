"use client";

interface InspectedRequest { request_id: string; method: string; path: string;
  headers: Record<string, string>; body_size_bytes: number; content_type: string;
  has_auth: boolean; auth_type: string | null; timestamp: string; }
interface RequestInspectorPanelProps { request: InspectedRequest; }

const methodColor: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-purple-600",
};

export function RequestInspectorPanel({ request: r }: RequestInspectorPanelProps) {
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`font-mono font-bold ${methodColor[r.method] ?? ""}`}>{r.method}</span>
          <span className="font-mono text-sm">{r.path}</span>
        </div>
        <span className="font-mono text-xs text-gray-400">{r.request_id}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div><span className="text-gray-400">Content-Type: </span>{r.content_type || "—"}</div>
        <div><span className="text-gray-400">Body: </span>{r.body_size_bytes} bytes</div>
        <div><span className="text-gray-400">Auth: </span>{r.has_auth ? `${r.auth_type} ✓` : "None"}</div>
        <div><span className="text-gray-400">Time: </span>{new Date(r.timestamp).toLocaleTimeString()}</div>
      </div>
      <details>
        <summary className="cursor-pointer text-xs text-gray-400">Headers ({Object.keys(r.headers).length})</summary>
        <div className="mt-1 space-y-0.5 font-mono text-xs">
          {Object.entries(r.headers).map(([k, v]) => (
            <div key={k}><span className="text-blue-500">{k}</span>: {v}</div>
          ))}
        </div>
      </details>
    </div>
  );
}
