"use client";

interface FeedEntry { appName: string; appIcon: string; version: string;
  title: string; type: string; date: string; }
interface ChangelogFeedPageProps { entries: FeedEntry[]; total: number;
  appsWithUpdates: number; }

const typeIcons: Record<string, string> = {
  added: "✨", fixed: "🐛", changed: "🔄", removed: "🗑️", security: "🔒",
};

export function ChangelogFeedPage({ entries, total, appsWithUpdates }: ChangelogFeedPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📋 What&apos;s New</h2>
        <span className="text-xs text-gray-400">{appsWithUpdates} apps updated · {total} changes</span>
      </div>
      <div className="space-y-3">
        {entries.map((e, i) => (
          <div key={i} className="flex items-start gap-3 rounded-lg border p-3 dark:border-gray-700">
            <span className="text-xl">{e.appIcon}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">{e.appName}</span>
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">v{e.version}</span>
              </div>
              <p className="mt-0.5 text-sm">{typeIcons[e.type] ?? "📌"} {e.title}</p>
              <p className="mt-0.5 text-xs text-gray-400">{e.date}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
