"use client";

interface DeprecatedEndpointInfo {
  endpoint_id: string;
  method: string;
  path: string;
  replacement: string;
  days_until_sunset: number;
  is_sunset: boolean;
  request_count: number;
}

interface APIDeprecationCardProps {
  endpoints: DeprecatedEndpointInfo[];
  appName: string;
}

export default function APIDeprecationCard({ endpoints, appName }: APIDeprecationCardProps) {
  const sunset = endpoints.filter((e) => e.is_sunset).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⏳ API Deprecations
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{endpoints.length} deprecated</span>
          {sunset > 0 && <p className="text-[10px] text-red-500">{sunset} sunset</p>}
        </div>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecations</p>
      ) : (
        <div className="space-y-2">
          {endpoints.map((ep) => (
            <div
              key={ep.endpoint_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[10px] font-medium text-gray-600 dark:bg-gray-800">
                    {ep.method}
                  </span>
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                    {ep.path}
                  </span>
                </div>
                <span
                  className={`text-[11px] ${ep.is_sunset ? "font-medium text-red-500" : "text-orange-500"}`}
                >
                  {ep.is_sunset ? "sunset" : `${ep.days_until_sunset}d left`}
                </span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                {ep.replacement ? <span>→ {ep.replacement}</span> : <span>no replacement</span>}
                <span>{ep.request_count} reqs</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
