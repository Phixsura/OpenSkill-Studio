"use client";

interface Endpoint { path: string; method: string; requestCount: number; avgMs: number; status: string; firstSeen: string; }
interface Props { endpoints: Endpoint[]; totalDiscovered: number; documented: number; undocumented: number; newCount: number; appName: string; }

const statusColors: Record<string, string> = { discovered: "bg-blue-100 text-blue-700", documented: "bg-green-100 text-green-700", deprecated: "bg-gray-200 text-gray-500" };
const methodColors: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-amber-600", DELETE: "text-red-600" };

export default function APIDeveloperPlatformSDKConsumerApiEndpointDiscoveryCard({ endpoints, totalDiscovered, documented, undocumented, newCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Endpoint Discovery</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalDiscovered} discovered · {documented} documented · {undocumented} undocumented{newCount > 0 ? ` · ${newCount} new` : ""}</p>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints discovered</p>
      ) : (
        <div className="space-y-1">
          {endpoints.slice(0, 8).map((e, i) => (
            <div key={i} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <span className={`font-bold ${methodColors[e.method] ?? "text-gray-500"}`}>{e.method}</span>
                <code className="text-gray-600 dark:text-gray-400">{e.path}</code>
              </div>
              <div className="flex gap-2">
                <span className="text-gray-400">{e.requestCount} req</span>
                <span className={`rounded px-1 py-0.5 text-[8px] ${statusColors[e.status] ?? ""}`}>{e.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
