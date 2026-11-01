"use client";

interface MW { id: string; name: string; type: string; order: number; enabled: boolean; }
interface Props { middlewares: MW[]; consumerId: string; appName: string; }

const typeColors: Record<string, string> = {
  auth: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  rate_limit: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  cors: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  logging: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  cache: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiGatewayMiddlewareCard({ middlewares, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Gateway Middleware</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {middlewares.length} middlewares</p>
      </div>
      {middlewares.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No middleware configured</p>
      ) : (
        <div className="space-y-1">
          {middlewares.map((m, i) => (
            <div key={m.id} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800 ${!m.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span className="text-[9px] text-gray-400">{i + 1}</span>
                <span className="text-gray-700 dark:text-gray-300">{m.name}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] ${typeColors[m.type] ?? "bg-gray-200 text-gray-600"}`}>{m.type}</span>
              </div>
              <span className={m.enabled ? "text-green-500" : "text-gray-400"}>{m.enabled ? "●" : "○"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
