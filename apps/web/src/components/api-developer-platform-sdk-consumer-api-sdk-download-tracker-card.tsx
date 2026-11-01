"use client";

interface Props { totalDownloads: number; byLanguage: Record<string, number>; mostPopular: string; latestVersion: string; appName: string; }

const langIcons: Record<string, string> = { typescript: "TS", python: "PY", go: "GO", java: "JV", ruby: "RB", csharp: "C#", php: "PHP", rust: "RS", swift: "SW", kotlin: "KT" };
const langColors: Record<string, string> = {
  typescript: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  python: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  go: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400",
  java: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  ruby: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKConsumerApiSdkDownloadTrackerCard({ totalDownloads, byLanguage, mostPopular, latestVersion, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 SDK Downloads</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · Latest: {latestVersion || "—"}</p>
        </div>
        <div className="text-lg font-bold text-gray-900 dark:text-gray-100">{totalDownloads.toLocaleString()}</div>
      </div>
      {Object.keys(byLanguage).length === 0 ? (
        <p className="text-center text-sm text-gray-400">No downloads yet</p>
      ) : (
        <div className="space-y-1">
          {Object.entries(byLanguage).sort((a, b) => b[1] - a[1]).map(([lang, count]) => (
            <div key={lang} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1">
                <span className={`rounded px-1.5 py-0.5 text-[9px] font-bold ${langColors[lang] ?? "bg-gray-200 text-gray-600"}`}>{langIcons[lang] ?? lang}</span>
                <span className="text-gray-700 dark:text-gray-300">{lang}{lang === mostPopular ? " ⭐" : ""}</span>
              </div>
              <span className="text-gray-400">{count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
