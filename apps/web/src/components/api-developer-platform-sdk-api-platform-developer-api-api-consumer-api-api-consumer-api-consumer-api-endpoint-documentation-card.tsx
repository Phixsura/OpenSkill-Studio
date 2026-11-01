"use client";

interface Endpoint { id: string; method: string; path: string; summary: string; tags: string[]; deprecated: boolean; }
interface Props { endpoints: Endpoint[]; tags: string[]; appName: string; }

const methodColors: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  PUT: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  PATCH: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentationCard({ endpoints, tags, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📚 Endpoint Docs</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoints.length} endpoints · {tags.length} tags</p>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints documented</p>
      ) : (
        <div className="space-y-1">
          {endpoints.slice(0, 8).map((e) => (
            <div key={e.id} className={`flex items-center gap-2 rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800 ${e.deprecated ? "opacity-50 line-through" : ""}`}>
              <span className={`rounded px-1 py-0.5 text-[9px] font-bold ${methodColors[e.method] ?? "bg-gray-200 text-gray-600"}`}>{e.method}</span>
              <code className="text-gray-600 dark:text-gray-400">{e.path}</code>
              <span className="truncate text-gray-400">{e.summary}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
