"use client";

interface Endpoint { id: string; method: string; path: string; summary: string; authRequired: boolean; }
interface Category { name: string; endpoints: Endpoint[]; }
interface Props { categories: Category[]; totalEndpoints: number; appName: string; }

const methodColors: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  PUT: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorerCard({ categories, totalEndpoints, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 API Explorer</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalEndpoints} endpoints · {categories.length} categories</p>
      </div>
      {categories.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints</p>
      ) : (
        <div className="space-y-3">
          {categories.map((c) => (
            <div key={c.name}>
              <div className="mb-1 text-[11px] font-semibold text-gray-500 dark:text-gray-400">{c.name}</div>
              <div className="space-y-0.5">
                {c.endpoints.slice(0, 4).map((e) => (
                  <div key={e.id} className="flex items-center gap-1 text-[10px]">
                    <span className={`rounded px-1 py-0.5 text-[9px] font-bold ${methodColors[e.method] ?? "bg-gray-200 text-gray-600"}`}>{e.method}</span>
                    <code className="text-gray-600 dark:text-gray-400">{e.path}</code>
                    {e.authRequired && <span className="text-[8px] text-gray-400">🔒</span>}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
