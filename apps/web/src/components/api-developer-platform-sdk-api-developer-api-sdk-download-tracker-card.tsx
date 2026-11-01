"use client";

interface Props { totalDownloads: number; languageBreakdown: Record<string, number>; popularSDKs: [string, number][]; appName: string; }

const langColor: Record<string, string> = { python: "bg-blue-100 text-blue-700", javascript: "bg-yellow-100 text-yellow-700", typescript: "bg-blue-100 text-blue-700", go: "bg-cyan-100 text-cyan-700", ruby: "bg-red-100 text-red-700", java: "bg-orange-100 text-orange-700" };

export default function APIDeveloperPlatformSDKApiDeveloperApiSDKDownloadTrackerCard({ totalDownloads, languageBreakdown, popularSDKs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 SDK Downloads</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{totalDownloads.toLocaleString()}</span>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(languageBreakdown).map(([lang, count]) => (
          <span key={lang} className={`rounded px-1.5 py-0.5 text-[10px] ${langColor[lang] ?? "bg-gray-100 text-gray-600"}`}>{lang}: {count.toLocaleString()}</span>
        ))}
      </div>
      {popularSDKs.length > 0 && (
        <div className="space-y-1">
          {popularSDKs.map(([name, count]) => (
            <div key={name} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{name}</span>
              <span className="text-gray-400">{count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
