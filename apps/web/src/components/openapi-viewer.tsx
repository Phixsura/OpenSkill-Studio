"use client";

interface Endpoint { path: string; method: string; summary: string; }
interface OpenApiViewerProps { title: string; version: string; endpoints: Endpoint[]; serverUrl: string; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-700", POST: "bg-blue-100 text-blue-700",
  PUT: "bg-yellow-100 text-yellow-700", DELETE: "bg-red-100 text-red-700",
  PATCH: "bg-purple-100 text-purple-700",
};

export function OpenApiViewer({ title, version, endpoints, serverUrl }: OpenApiViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{title}</h3>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700">{version}</span>
      </div>
      <p className="mt-1 text-xs text-gray-400">{serverUrl}</p>
      <ul className="mt-3 space-y-1">
        {endpoints.map((ep, i) => (
          <li key={i} className="flex items-center gap-2 text-sm">
            <span className={`rounded px-1.5 py-0.5 text-xs font-mono ${METHOD_COLORS[ep.method] || "bg-gray-100"}`}>{ep.method}</span>
            <code className="text-xs text-gray-600 dark:text-gray-400">{ep.path}</code>
            <span className="ml-auto text-xs text-gray-400">{ep.summary}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
