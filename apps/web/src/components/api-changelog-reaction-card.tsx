"use client";

interface ReactionEntry {
  entry_id: string;
  title: string;
  counts: Record<string, number>;
  total: number;
}

interface APIChangelogReactionCardProps {
  entries: ReactionEntry[];
  appName: string;
}

export default function APIChangelogReactionCard({ entries, appName }: APIChangelogReactionCardProps) {
  const totalReactions = entries.reduce((s, e) => s + e.total, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">😊 Changelog Reactions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalReactions} reactions</span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No reactions yet</p>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <div key={e.entry_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <p className="text-xs text-gray-700 dark:text-gray-300">{e.title}</p>
              <div className="mt-1 flex gap-2">
                {Object.entries(e.counts).map(([emoji, count]) => (
                  <span key={emoji} className="rounded bg-gray-100 px-1.5 py-0.5 text-[11px] dark:bg-gray-800">
                    {emoji} {count}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
