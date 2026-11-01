"use client";

interface Endpoint { method: string; path: string; operationId: string | null; hasSummary: boolean; tags: string[]; }
interface OpenApiViewerProps { title: string; version: string; valid: boolean;
  endpoints: Endpoint[]; errors: string[]; warnings: string[]; }

const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  PATCH: "bg-orange-500", DELETE: "bg-red-500",
};

export function OpenApiViewer({ title, version, valid, endpoints, errors, warnings }: OpenApiViewerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">{title || "API Spec"}</h3>
          <p className="text-xs text-gray-400">OpenAPI {version}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-xs ${valid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {valid ? "Valid" : `${errors.length} errors`}
        </span>
      </div>
      {warnings.length > 0 && <p className="text-xs text-yellow-600">⚠ {warnings.length} warnings</p>}
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-64 overflow-y-auto">
        {endpoints.map((ep, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-2">
            <span className={`rounded px-1.5 py-0.5 text-xs text-white font-mono ${methodColors[ep.method] ?? "bg-gray-500"}`}>{ep.method}</span>
            <span className="text-sm font-mono">{ep.path}</span>
            {ep.tags.map(t => <span key={t} className="rounded bg-gray-100 px-1 py-0.5 text-xs dark:bg-gray-800">{t}</span>)}
          </div>
        ))}
      </div>
    </div>
  );
}
