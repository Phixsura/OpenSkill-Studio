"use client";

interface FeedEntry {
  version: string;
  title: string;
  description: string;
  publishedAt: string;
  author: string;
  type: "major" | "minor" | "patch";
}

export function ExtensionChangelogFeed({
  extensionName,
  entries,
  rssUrl,
}: {
  extensionName: string;
  entries: FeedEntry[];
  rssUrl?: string;
}) {
  const typeConfig: Record<string, { color: string; label: string }> = {
    major: { color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300", label: "Major" },
    minor: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300", label: "Minor" },
    patch: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300", label: "Patch" },
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📰 {extensionName} Updates</h2>
        {rssUrl && (
          <a href={rssUrl} className="flex items-center gap-1 text-xs text-orange-500 hover:underline">
            📡 RSS Feed
          </a>
        )}
      </div>

      <div className="space-y-3">
        {entries.map((entry) => {
          const cfg = typeConfig[entry.type];
          return (
            <div key={entry.version} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-mono font-bold text-blue-600 dark:text-blue-400">v{entry.version}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
                <span className="text-xs text-gray-400">· {entry.publishedAt}</span>
                <span className="text-xs text-gray-400">· by {entry.author}</span>
              </div>
              <h3 className="font-semibold text-sm">{entry.title}</h3>
              <p className="text-sm text-gray-500 mt-1">{entry.description}</p>
            </div>
          );
        })}
      </div>

      {entries.length === 0 && (
        <div className="text-center text-gray-400 py-6 text-sm">No updates yet</div>
      )}
    </div>
  );
}
