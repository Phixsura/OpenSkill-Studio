"use client";

interface Version { version: string; release_date: string; summary: string; is_major: boolean; download_count: number; }
interface VersionHistoryTimelineProps { appName: string; versions: Version[]; }

export function VersionHistoryTimeline({ appName, versions }: VersionHistoryTimelineProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{appName} — Version History</h2>
      <div className="relative border-l-2 border-gray-200 pl-6 dark:border-gray-700">
        {versions.map((v, i) => (
          <div key={v.version} className="relative mb-6">
            <div className={`absolute -left-[1.9rem] h-3 w-3 rounded-full ${v.is_major ? "bg-blue-600" : "bg-gray-400"}`} />
            <div className="flex items-baseline gap-2">
              <span className={`font-mono text-sm font-bold ${v.is_major ? "text-blue-600" : ""}`}>v{v.version}</span>
              <span className="text-xs text-gray-400">{new Date(v.release_date).toLocaleDateString()}</span>
            </div>
            <p className="mt-0.5 text-sm text-gray-600 dark:text-gray-300">{v.summary}</p>
            <span className="mt-1 inline-block text-xs text-gray-400">{v.download_count.toLocaleString()} downloads</span>
          </div>
        ))}
      </div>
    </div>
  );
}
