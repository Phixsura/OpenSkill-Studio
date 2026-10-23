"use client";

interface TimelineEntry { version: string; date: string; title: string; features: number;
  fixes: number; breaking: number; total_changes: number; is_major: boolean; }
interface ChangelogTimelineViewProps { timeline: TimelineEntry[]; totalVersions: number;
  totalChanges: number; }

export function ChangelogTimelineView({ timeline, totalVersions, totalChanges }: ChangelogTimelineViewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Changelog Timeline</h2>
        <span className="text-xs text-gray-400">{totalVersions} versions · {totalChanges} changes</span>
      </div>
      <div className="relative border-l-2 border-gray-200 pl-6 dark:border-gray-700">
        {timeline.map(t => (
          <div key={t.version} className="relative mb-6">
            <div className={`absolute -left-[1.9rem] h-4 w-4 rounded-full ${t.is_major ? "bg-blue-600" : "bg-gray-400"}`} />
            <div className="flex items-baseline gap-2">
              <span className={`font-mono text-sm font-bold ${t.is_major ? "text-blue-600" : ""}`}>v{t.version}</span>
              <span className="text-xs text-gray-400">{t.date}</span>
              {t.breaking > 0 && <span className="rounded bg-red-100 px-1 py-0.5 text-[10px] text-red-700 dark:bg-red-900/30">Breaking</span>}
            </div>
            <p className="mt-0.5 text-sm">{t.title}</p>
            <div className="mt-1 flex gap-2 text-xs text-gray-400">
              {t.features > 0 && <span>✨ {t.features} features</span>}
              {t.fixes > 0 && <span>🐛 {t.fixes} fixes</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
