"use client";

interface VersionInfo { version: string; status: string; consumers_using: number; }
interface EndpointInfo { endpoint: string; method: string; versions: VersionInfo[]; default_version: string; }
interface Props { endpoints: EndpointInfo[]; appName: string; }

const statusColor: Record<string, string> = { active: "text-green-600 dark:text-green-400", deprecated: "text-yellow-600 dark:text-yellow-400", sunset: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointVersioningCard({ endpoints, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔢 Endpoint Versioning</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoints.length} endpoints</p>
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No versioned endpoints</p>
      ) : (
        <div className="space-y-2">
          {endpoints.map((e) => (
            <div key={`${e.method}-${e.endpoint}`} className="text-[11px]">
              <div className="font-medium text-gray-700 dark:text-gray-300">{e.method} {e.endpoint}</div>
              <div className="flex gap-1 mt-0.5">
                {e.versions.map((v) => (
                  <span key={v.version} className={`rounded px-1 text-[9px] ${v.version === e.default_version ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 font-medium" : "bg-gray-100 text-gray-500 dark:bg-gray-800"} ${statusColor[v.status] ?? ""}`}>{v.version}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
