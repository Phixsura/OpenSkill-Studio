"use client";

interface ChangelogRssFeedLinkProps { appName: string; appId: string; feedUrl: string; onCopy: () => void; }

export function ChangelogRssFeedLink({ appName, appId, feedUrl, onCopy }: ChangelogRssFeedLinkProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border p-4 dark:border-gray-700">
      <span className="text-2xl">📡</span>
      <div className="flex-1">
        <p className="text-sm font-medium">{appName} Changelog Feed</p>
        <p className="mt-0.5 truncate font-mono text-xs text-gray-400">{feedUrl}</p>
      </div>
      <div className="flex gap-2">
        <button onClick={onCopy} className="rounded border px-2.5 py-1 text-xs dark:border-gray-600">Copy URL</button>
        <a href={feedUrl} target="_blank" rel="noopener noreferrer"
          className="rounded bg-orange-500 px-2.5 py-1 text-xs text-white">Subscribe</a>
      </div>
    </div>
  );
}
