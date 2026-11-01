"use client";

interface VersionInfo { version: string; status: string; supported: boolean; }
interface Props { versions: VersionInfo[]; defaultVersion: string; deprecatedCount: number; appName: string; }

const statusStyle: Record<string, string> = { stable: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400", beta: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400", deprecated: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400", sunset: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiVersionNegotiatorCard({ versions, defaultVersion, deprecatedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔢 API Versions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — default: {defaultVersion}</p>
        </div>
        {deprecatedCount > 0 && <span className="text-[10px] text-amber-600 dark:text-amber-400">⚠️ {deprecatedCount} deprecated</span>}
      </div>
      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No versions</p>
      ) : (
        <div className="space-y-1">
          {versions.map((v) => (
            <div key={v.version} className="flex items-center justify-between text-[11px]">
              <span className="font-mono font-medium text-gray-700 dark:text-gray-300">{v.version}</span>
              <span className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${statusStyle[v.status] ?? ""}`}>{v.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
