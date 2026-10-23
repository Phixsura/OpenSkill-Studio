"use client";

interface Release { version: string; date: string; title: string;
  changesCount: number; breakingCount: number; highlight: boolean; tags: string[]; }
interface ReleaseTimelineProps { releases: Release[]; }

export function ReleaseTimeline({ releases }: ReleaseTimelineProps) {
  return (
    <div className="space-y-0">
      {releases.map((r, i) => (
        <div key={r.version} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div className={`w-4 h-4 rounded-full border-2 ${
              r.highlight ? "bg-blue-500 border-blue-500" : "bg-white dark:bg-gray-900 border-gray-300 dark:border-gray-600"
            }`} />
            {i < releases.length - 1 && <div className="w-0.5 flex-1 bg-gray-200 dark:bg-gray-700" />}
          </div>
          <div className="pb-6 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-bold">v{r.version}</span>
              <span className="text-xs text-gray-400">{r.date}</span>
              {r.breakingCount > 0 && <span className="text-xs px-1.5 py-0.5 rounded bg-red-100 text-red-700">Breaking</span>}
              {r.tags.map(t => <span key={t} className="text-xs px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">{t}</span>)}
            </div>
            <p className="text-sm">{r.title}</p>
            <p className="text-xs text-gray-400">{r.changesCount} changes</p>
          </div>
        </div>
      ))}
    </div>
  );
}
