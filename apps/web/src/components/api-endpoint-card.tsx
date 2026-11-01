"use client";

interface ApiEndpointCardProps {
  method: string;
  path: string;
  summary: string;
  scopes?: string[];
}

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-800", POST: "bg-blue-100 text-blue-800",
  PUT: "bg-yellow-100 text-yellow-800", PATCH: "bg-orange-100 text-orange-800",
  DELETE: "bg-red-100 text-red-800",
};

export function ApiEndpointCard({ method, path, summary, scopes }: ApiEndpointCardProps) {
  return (
    <div className="flex items-center gap-3 rounded border border-gray-200 p-3 dark:border-gray-700">
      <span className={`rounded px-2 py-0.5 text-xs font-bold ${METHOD_COLORS[method] ?? "bg-gray-100"}`}>{method}</span>
      <code className="flex-1 text-sm font-mono">{path}</code>
      <span className="text-sm text-gray-500">{summary}</span>
      {scopes && scopes.length > 0 && (
        <div className="flex gap-1">
          {scopes.map(s => <span key={s} className="rounded bg-gray-100 px-1 py-0.5 text-xs dark:bg-gray-800">{s}</span>)}
        </div>
      )}
    </div>
  );
}
