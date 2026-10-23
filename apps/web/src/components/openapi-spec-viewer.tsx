"use client";

interface Endpoint { path: string; method: string; description: string; }
interface OpenApiSpecViewerProps { appName: string; version: string; endpoints: Endpoint[];
  pathCount: number; onDownload: () => void; }

const methodColor: Record<string, string> = {
  get: "bg-green-100 text-green-700 dark:bg-green-900/30", post: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  put: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", delete: "bg-red-100 text-red-700 dark:bg-red-900/30",
  patch: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
};

export function OpenApiSpecViewer({ appName, version, endpoints, pathCount, onDownload }: OpenApiSpecViewerProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{appName} API</h2>
          <p className="text-xs text-gray-400">v{version} · {pathCount} paths · {endpoints.length} operations</p>
        </div>
        <button onClick={onDownload} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">
          Download Spec
        </button>
      </div>
      <div className="space-y-1.5">
        {endpoints.map((ep, i) => (
          <div key={i} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
            <span className={`rounded px-2 py-0.5 font-mono text-xs font-bold uppercase ${methodColor[ep.method.toLowerCase()] ?? ""}`}>
              {ep.method}
            </span>
            <span className="font-mono text-sm">{ep.path}</span>
            <span className="ml-auto text-xs text-gray-400">{ep.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
