"use client";

interface LangDownload { language: string; downloads: number; }
interface Props { languages: LangDownload[]; totalDownloads: number; appName: string; }

export default function APIDeveloperSDKDownloadCard({ languages, totalDownloads, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📥 SDK Downloads</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{totalDownloads.toLocaleString()}</span>
      </div>
      {languages.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No downloads yet</p>
      ) : (
        <div className="space-y-1.5">
          {languages.map((l) => {
            const pct = totalDownloads > 0 ? Math.round((l.downloads / totalDownloads) * 100) : 0;
            return (
              <div key={l.language}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{l.language}</span>
                  <span className="text-gray-400">{l.downloads.toLocaleString()} ({pct}%)</span>
                </div>
                <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className="h-1 rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
