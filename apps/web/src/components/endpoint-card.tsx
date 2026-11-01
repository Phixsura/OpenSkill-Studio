"use client";

interface EndpointCardProps { method: string; path: string; summary: string; authRequired: boolean; curlExample: string; onTry: () => void; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-700", POST: "bg-blue-100 text-blue-700",
  PUT: "bg-yellow-100 text-yellow-700", DELETE: "bg-red-100 text-red-700",
  PATCH: "bg-purple-100 text-purple-700",
};

export function EndpointCard({ method, path, summary, authRequired, curlExample, onTry }: EndpointCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <span className={`rounded px-2 py-0.5 text-xs font-mono font-bold ${METHOD_COLORS[method] || "bg-gray-100"}`}>{method}</span>
        <code className="text-sm">{path}</code>
        {authRequired && <span className="text-xs text-gray-400">🔒</span>}
      </div>
      <p className="mt-1 text-sm text-gray-500">{summary}</p>
      <details className="mt-2">
        <summary className="cursor-pointer text-xs text-blue-600">cURL example</summary>
        <pre className="mt-1 rounded bg-gray-50 p-2 text-xs dark:bg-gray-800">{curlExample}</pre>
      </details>
      <button onClick={onTry} className="mt-2 rounded bg-blue-600 px-3 py-1 text-xs text-white">Try it →</button>
    </div>
  );
}
