"use client";

interface LanguageCount { language: string; downloads: number; }
interface VersionCount { version: string; downloads: number; }
interface Props { sdkName: string; totalDownloads: number; languages: LanguageCount[]; versions: VersionCount[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiSdkDownloadTrackerCard({ sdkName, totalDownloads, languages, versions, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📥 SDK Downloads</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {sdkName}</p>
        </div>
        <span className="text-lg font-bold text-gray-900 dark:text-gray-100">{totalDownloads.toLocaleString()}</span>
      </div>
      <div className="mb-2 space-y-1">
        {versions.map((v) => (
          <div key={v.version} className="flex items-center justify-between text-[11px]">
            <span className="font-mono text-gray-700 dark:text-gray-300">{v.version}</span>
            <span className="text-gray-400">{v.downloads.toLocaleString()}</span>
          </div>
        ))}
      </div>
      {languages.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {languages.map((l) => (
            <span key={l.language} className="rounded bg-blue-100 px-1.5 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{l.language}: {l.downloads.toLocaleString()}</span>
          ))}
        </div>
      )}
    </div>
  );
}
