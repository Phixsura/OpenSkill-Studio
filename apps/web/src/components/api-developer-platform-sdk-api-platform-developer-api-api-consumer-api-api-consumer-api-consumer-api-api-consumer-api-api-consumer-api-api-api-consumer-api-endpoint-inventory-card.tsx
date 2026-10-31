"use client";

interface Endpoint { id: string; method: string; path: string; status: string; version: string; }
interface Summary { total: number; byMethod: Record<string, number>; byStatus: Record<string, number>; }
interface Props { endpoints: Endpoint[]; summary: Summary; appName: string; }

const methodColors: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-amber-600", DELETE: "text-red-600", PATCH: "text-purple-600" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventoryCard({ endpoints, summary, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Endpoint Inventory</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {summary.total} endpoints</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(summary.byMethod).map(([m, c]) => (
          <span key={m} className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">{m}: {c}</span>
        ))}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints</p>
      ) : (
        <div className="space-y-0.5">
          {endpoints.slice(0, 8).map((e) => (
            <div key={e.id} className="flex items-center gap-1 text-[10px]">
              <span className={`font-bold ${methodColors[e.method] ?? "text-gray-500"}`}>{e.method}</span>
              <code className="text-gray-600 dark:text-gray-400">{e.path}</code>
              {e.status !== "active" && <span className="text-[8px] text-amber-500">{e.status}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
