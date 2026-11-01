"use client";

interface VersionInfo { version: string; language: string; status: string; downloads: number; active_users: number; }
interface Props { versions: VersionInfo[]; languages: string[]; deprecatedInUse: number; appName: string; }

const sBadge: Record<string, string> = { stable: "bg-green-100 text-green-700", beta: "bg-purple-100 text-purple-700", deprecated: "bg-yellow-100 text-yellow-700", eol: "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManagerCard({ versions, languages, deprecatedInUse, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 SDK Versions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {languages.length} languages</p>
        </div>
        {deprecatedInUse > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{deprecatedInUse} deprecated in use</span>}
      </div>
      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SDK versions</p>
      ) : (
        <div className="space-y-1.5">
          {versions.slice(0, 6).map((v) => (
            <div key={`${v.language}-${v.version}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-700 dark:text-gray-300">{v.language}</span>
                <span className="text-gray-400">v{v.version}</span>
                <span className={`rounded px-1 py-0.5 text-[8px] ${sBadge[v.status] ?? ""}`}>{v.status}</span>
              </div>
              <span className="text-gray-400">{v.downloads.toLocaleString()} dl · {v.active_users} active</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
