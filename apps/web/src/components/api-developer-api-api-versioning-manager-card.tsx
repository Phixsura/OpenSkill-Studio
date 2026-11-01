"use client";

interface VersionInfo { version: string; status: string; endpoints_count: number; traffic_pct: number; }
interface Props { versions: VersionInfo[]; appName: string; }

const sColor: Record<string, string> = { active: "bg-green-100 text-green-700", deprecated: "bg-yellow-100 text-yellow-700", sunset: "bg-red-100 text-red-700" };

export default function APIDeveloperAPIApiVersioningManagerCard({ versions, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 API Versioning</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {versions.length} versions</p>
      </div>
      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API versions</p>
      ) : (
        <div className="space-y-2">
          {versions.map((v) => (
            <div key={v.version} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-bold text-gray-900 dark:text-gray-100">{v.version}</span>
                <span className={`rounded-full px-1.5 py-0.5 text-[9px] font-medium ${sColor[v.status] ?? ""}`}>{v.status}</span>
              </div>
              <div className="text-right text-[10px] text-gray-400">
                <span>{v.endpoints_count} endpoints</span>
                {v.traffic_pct > 0 && <span className="ml-2">{v.traffic_pct}% traffic</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
