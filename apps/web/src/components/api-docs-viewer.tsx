"use client";

interface PathOp { summary: string; description: string; tag: string; authRequired: boolean; }
interface ApiDocsViewerProps { title: string; version: string;
  paths: Record<string, Record<string, PathOp>>; tags: string[];
  operationCount: number; }

const METHOD_BADGE: Record<string, string> = {
  get: "bg-green-100 text-green-700", post: "bg-blue-100 text-blue-700",
  put: "bg-yellow-100 text-yellow-700", delete: "bg-red-100 text-red-700",
  patch: "bg-orange-100 text-orange-700",
};

export function ApiDocsViewer({ title, version, paths, tags, operationCount }: ApiDocsViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">{title}</h3>
        <div className="flex gap-2 mt-1 text-xs text-gray-400">
          <span>v{version}</span><span>·</span>
          <span>{operationCount} operations</span><span>·</span>
          <span>{tags.join(", ")}</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(paths).map(([path, methods]) =>
          Object.entries(methods).map(([method, op]) => (
            <div key={`${method}-${path}`} className="px-4 py-3">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-1.5 py-0.5 rounded font-bold uppercase ${METHOD_BADGE[method] || ""}`}>{method}</span>
                <span className="text-sm font-mono">{path}</span>
                {op.authRequired && <span className="text-xs text-gray-400">🔒</span>}
              </div>
              <p className="text-sm text-gray-500">{op.summary}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
