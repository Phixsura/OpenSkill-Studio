"use client";

interface EndpointVersionInfo {
  method: string;
  path: string;
  version: string;
  deprecated: boolean;
}

interface APIEndpointVersionCardProps {
  endpoints: EndpointVersionInfo[];
  appName: string;
}

export default function APIEndpointVersionCard({ endpoints, appName }: APIEndpointVersionCardProps) {
  const deprecated = endpoints.filter((e) => e.deprecated).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📌 Endpoint Versions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{endpoints.length} endpoints</span>
          {deprecated > 0 && <p className="text-[10px] text-yellow-600">{deprecated} deprecated</p>}
        </div>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoint versions</p>
      ) : (
        <div className="space-y-1">
          {endpoints.map((e, i) => (
            <div key={i} className={`flex items-center justify-between text-[11px] ${e.deprecated ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800">{e.method}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{e.path}</span>
              </div>
              <span className="text-gray-400">{e.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
