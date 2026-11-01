"use client";

interface OpenApiSpecViewerProps { title: string; version: string; endpointCount: number;
  pathCount: number; tags: string[]; byMethod: Record<string, number>; }

const METHOD_COLORS: Record<string, string> = {
  get: "bg-green-500", post: "bg-blue-500", put: "bg-yellow-500",
  patch: "bg-orange-500", delete: "bg-red-500",
};

export function OpenApiSpecViewer({ title, version, endpointCount, pathCount, tags, byMethod }: OpenApiSpecViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">{title}</h3>
          <div className="text-xs text-gray-400">v{version} · OpenAPI 3.0</div>
        </div>
        <span className="text-xs text-gray-400">{endpointCount} endpoints · {pathCount} paths</span>
      </div>
      <div className="flex gap-2 px-4 py-2 border-b dark:border-gray-700 flex-wrap">
        {Object.entries(byMethod).map(([method, count]) => (
          <span key={method} className={`px-2 py-0.5 text-[10px] text-white rounded uppercase ${METHOD_COLORS[method] ?? "bg-gray-500"}`}>
            {method} ×{count}
          </span>
        ))}
      </div>
      <div className="p-4">
        <div className="text-xs text-gray-400 mb-1">Tags</div>
        <div className="flex flex-wrap gap-1">
          {tags.map(t => (
            <span key={t} className="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 rounded">{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
