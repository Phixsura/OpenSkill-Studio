"use client";

interface ApiDocsEndpointProps { method: string; path: string; summary: string; scopes: string[]; curlExample: string; }

const METHOD_COLORS: Record<string, string> = { GET: "bg-green-100 text-green-800", POST: "bg-blue-100 text-blue-800", PUT: "bg-yellow-100 text-yellow-800", DELETE: "bg-red-100 text-red-800" };

export function ApiDocsEndpoint({ method, path, summary, scopes, curlExample }: ApiDocsEndpointProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-2 flex items-center gap-2">
        <span className={`rounded px-2 py-0.5 text-xs font-bold ${METHOD_COLORS[method] ?? "bg-gray-100"}`}>{method}</span>
        <code className="text-sm">{path}</code>
      </div>
      <p className="mb-2 text-sm text-gray-600">{summary}</p>
      {scopes.length > 0 && <div className="mb-2 flex gap-1">{scopes.map(s => <span key={s} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{s}</span>)}</div>}
      <pre className="overflow-x-auto rounded bg-gray-900 p-3 text-xs text-green-400"><code>{curlExample}</code></pre>
    </div>
  );
}
