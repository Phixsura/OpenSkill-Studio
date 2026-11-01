"use client";

interface EndpointHealthInfo {
  method: string;
  path: string;
  total: number;
  error_rate: number;
  is_degraded: boolean;
}

interface APIEndpointHealthCardProps {
  endpoints: EndpointHealthInfo[];
  appName: string;
}

export default function APIEndpointHealthCard({ endpoints, appName }: APIEndpointHealthCardProps) {
  const degraded = endpoints.filter((e) => e.is_degraded).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Endpoint Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{endpoints.length} endpoints</span>
          {degraded > 0 && <p className="text-[10px] text-red-500">{degraded} degraded</p>}
        </div>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoint data</p>
      ) : (
        <div className="space-y-1">
          {endpoints.map((e) => (
            <div key={`${e.method}-${e.path}`} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${e.is_degraded ? "bg-red-500" : "bg-green-500"}`} />
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{e.method}</span>
                <span className="font-mono text-[11px] text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <span className={`text-[10px] ${e.error_rate > 5 ? "text-red-500" : "text-gray-400"}`}>{e.error_rate}% err</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
