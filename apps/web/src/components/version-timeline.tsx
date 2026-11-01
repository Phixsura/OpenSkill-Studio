"use client";

interface VersionEntry { version: string; date: string; status: string; changelog: string; isLatest: boolean; }
interface VersionTimelineProps { entries: VersionEntry[]; }

export function VersionTimeline({ entries }: VersionTimelineProps) {
  if (entries.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No versions</p>;
  return (
    <div className="space-y-3">
      {entries.map(e => (
        <div key={e.version} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div className={`h-3 w-3 rounded-full ${e.isLatest ? "bg-green-500" : "bg-gray-300"}`} />
            <div className="flex-1 w-0.5 bg-gray-200 dark:bg-gray-700" />
          </div>
          <div className="pb-4">
            <div className="flex items-center gap-2">
              <span className="font-mono font-semibold">v{e.version}</span>
              {e.isLatest && <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-800">Latest</span>}
              <span className="text-xs text-gray-400">{e.date}</span>
            </div>
            {e.changelog && <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{e.changelog}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}
