"use client";

interface EndpointInfo { endpoint_id: string; method: string; path: string; version: string; status: string; documented: boolean; tags: string[]; }
interface Props { endpoints: EndpointInfo[]; stats: { total: number; active: number; deprecated: number; documented: number; undocumented: number }; appName: string; }

const mColor: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600", PATCH: "text-orange-600" };
const sColor: Record<string, string> = { active: "bg-green-100 text-green-700", deprecated: "bg-red-100 text-red-700", beta: "bg-purple-100 text-purple-700", internal: "bg-gray-100 text-gray-600" };

export default function APIDeveloperAPIApiDeveloperApiApiEndpointInventoryCard({ endpoints, stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Endpoint Inventory</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{stats.total} endpoints · {stats.documented} documented</span>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.slice(0, 8).map((e) => (
            <div key={e.endpoint_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`font-mono font-bold ${mColor[e.method] ?? "text-gray-500"}`}>{e.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <span className={`rounded px-1 py-0.5 text-[9px] ${sColor[e.status] ?? ""}`}>{e.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
