"use client";

interface EndpointInfo {
  method: string;
  path: string;
  description: string;
  auth_required: boolean;
  rate_limited: boolean;
  deprecated: boolean;
  tags: string[];
}

interface EndpointDiscoveryCardProps {
  endpoints: EndpointInfo[];
  appName: string;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  POST: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  PUT: "text-yellow-700 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30",
  DELETE: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
  PATCH: "text-orange-700 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30",
};

export default function EndpointDiscoveryCard({ endpoints, appName }: EndpointDiscoveryCardProps) {
  const deprecatedCount = endpoints.filter((e) => e.deprecated).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Endpoint Discovery
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{endpoints.length} endpoints</span>
          {deprecatedCount > 0 && (
            <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
              {deprecatedCount} deprecated
            </span>
          )}
        </div>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints discovered</p>
      ) : (
        <div className="space-y-1">
          {endpoints.map((e) => (
            <div
              key={`${e.method}-${e.path}`}
              className={`flex items-center justify-between rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50 ${e.deprecated ? "opacity-50" : ""}`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-1 py-0.5 text-[9px] font-bold ${METHOD_COLORS[e.method] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {e.method}
                </span>
                <span
                  className={`font-mono text-xs ${e.deprecated ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}`}
                >
                  {e.path}
                </span>
              </div>
              <div className="flex items-center gap-1">
                {e.auth_required && <span className="text-[9px] text-gray-400">🔒</span>}
                {e.rate_limited && <span className="text-[9px] text-gray-400">⏱</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
