"use client";

interface EndpointInfo { method: string; path: string; summary: string; category: string; }
interface Props { endpoints: EndpointInfo[]; categories: string[]; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-500", PATCH: "text-orange-500" };

export default function APIDeveloperAPIExplorerCard({ endpoints, categories, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔭 API Explorer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{endpoints.length} endpoints · {categories.length} categories</span>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints to explore</p>
      ) : (
        <div className="space-y-1">
          {endpoints.slice(0, 8).map((ep) => (
            <div key={`${ep.method}-${ep.path}`} className="flex items-center gap-2 text-[11px]">
              <span className={`w-10 font-mono font-medium ${mColor[ep.method] ?? "text-gray-500"}`}>{ep.method}</span>
              <span className="font-mono text-gray-700 dark:text-gray-300">{ep.path}</span>
            </div>
          ))}
          {endpoints.length > 8 && <p className="text-[10px] text-gray-400">+{endpoints.length - 8} more</p>}
        </div>
      )}
    </div>
  );
}
