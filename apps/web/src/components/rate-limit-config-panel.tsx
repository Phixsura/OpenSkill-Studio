"use client";

interface EndpointLimit { method: string; path: string; rpm: number; burst: number; custom: boolean; }
interface RateLimitConfigPanelProps { endpoints: EndpointLimit[]; customCount: number; onEdit: (idx: number) => void; }

const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500", DELETE: "bg-red-500",
};

export function RateLimitConfigPanel({ endpoints, customCount, onEdit }: RateLimitConfigPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Rate Limits</h3>
        <span className="text-xs text-gray-400">{customCount} custom</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {endpoints.map((ep, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs text-white font-mono ${methodColors[ep.method] ?? "bg-gray-500"}`}>{ep.method}</span>
              <code className="text-sm font-mono">{ep.path}</code>
              {ep.custom && <span className="text-xs text-blue-600">custom</span>}
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400">{ep.rpm} rpm · {ep.burst} burst</span>
              <button onClick={() => onEdit(i)} className="text-xs text-blue-600 hover:underline">Edit</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
