"use client";

interface CacheHeaders { ETag: string; "Cache-Control": string; Expires: string; Vary: string; }
interface CacheControlInspectorProps { headers: CacheHeaders; hitRate: number; onPurge: () => void; }

export function CacheControlInspector({ headers, hitRate, onPurge }: CacheControlInspectorProps) {
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Cache Inspector</h2>
        <span className={`text-sm font-medium ${hitRate >= 80 ? "text-green-600" : "text-yellow-600"}`}>
          {hitRate}% hit rate
        </span>
      </div>
      <div className="space-y-1 rounded bg-gray-900 p-3 font-mono text-xs">
        {Object.entries(headers).map(([k, v]) => (
          <div key={k}>
            <span className="text-blue-400">{k}</span>: <span className="text-green-400">{v}</span>
          </div>
        ))}
      </div>
      <button onClick={onPurge} className="w-full rounded border border-red-300 py-1.5 text-sm text-red-600">
        Purge Cache
      </button>
    </div>
  );
}
