"use client";

interface MockEndpoint { mock_id: string; path: string; method: string; status_code: number; url: string; delay_ms: number; }
interface MockServerBuilderProps { collectionName: string; baseUrl: string;
  endpoints: MockEndpoint[]; onAdd: () => void; onDelete: (id: string) => void; onCopyUrl: (url: string) => void; }

const methodBg: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30", POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  PUT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function MockServerBuilder({ collectionName, baseUrl, endpoints, onAdd, onDelete, onCopyUrl }: MockServerBuilderProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{collectionName}</h2>
          <p className="truncate font-mono text-xs text-gray-400">{baseUrl}</p>
        </div>
        <button onClick={onAdd} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add Endpoint</button>
      </div>
      <div className="space-y-1.5">
        {endpoints.map(ep => (
          <div key={ep.mock_id} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
            <span className={`rounded px-1.5 py-0.5 font-mono text-xs font-bold ${methodBg[ep.method] ?? ""}`}>{ep.method}</span>
            <span className="flex-1 font-mono text-sm">{ep.path}</span>
            <span className="text-xs text-gray-400">{ep.status_code}</span>
            {ep.delay_ms > 0 && <span className="text-xs text-yellow-500">{ep.delay_ms}ms</span>}
            <button onClick={() => onCopyUrl(ep.url)} className="text-xs text-blue-500">Copy</button>
            <button onClick={() => onDelete(ep.mock_id)} className="text-xs text-red-500">×</button>
          </div>
        ))}
      </div>
    </div>
  );
}
