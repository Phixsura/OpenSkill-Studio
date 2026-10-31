"use client";

interface CacheConfigProps { cacheControl: string; directives: string[]; cacheable: boolean;
  etag: string | null; }

export function CacheConfig({ cacheControl, directives, cacheable, etag }: CacheConfigProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Cache Configuration</h3>
      <div className="rounded-lg bg-gray-100 p-3 dark:bg-gray-800">
        <p className="text-xs text-gray-400 mb-1">Cache-Control</p>
        <code className="text-sm font-mono">{cacheControl}</code>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {directives.map(d => (
          <span key={d} className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{d}</span>
        ))}
      </div>
      <div className="flex items-center gap-3 text-xs">
        <span className={cacheable ? "text-green-600" : "text-red-600"}>
          {cacheable ? "✓ Cacheable" : "✗ No cache"}
        </span>
        {etag && <span className="text-gray-400">ETag: {etag}</span>}
      </div>
    </div>
  );
}
