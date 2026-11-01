"use client";

interface Endpoint { path: string; method: string; summary: string; tag: string; }
interface ApiDocsPanelProps { title: string; version: string; endpoints: Endpoint[];
  tags: string[]; docCoverage: number; }

const METHOD_STYLE: Record<string, string> = {
  get: "bg-green-100 text-green-700", post: "bg-blue-100 text-blue-700",
  put: "bg-yellow-100 text-yellow-700", delete: "bg-red-100 text-red-700",
};

export function ApiDocsPanel({ title, version, endpoints, tags, docCoverage }: ApiDocsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📖 {title} v{version}</h3>
        <span className="text-xs text-gray-400">{endpoints.length} endpoints · {docCoverage}% documented</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map((e, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-1.5 text-xs">
            <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold ${METHOD_STYLE[e.method.toLowerCase()] ?? ""}`}>{e.method}</span>
            <span className="font-mono">{e.path}</span>
            <span className="text-gray-400">{e.summary}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
