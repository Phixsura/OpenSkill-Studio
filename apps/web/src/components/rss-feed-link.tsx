"use client";

interface RssFeedLinkProps { feedUrl: string; atomUrl?: string; appName: string; entryCount: number; }

export function RssFeedLink({ feedUrl, atomUrl, appName, entryCount }: RssFeedLinkProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border px-4 py-3 dark:border-gray-700">
      <span className="text-xl">📡</span>
      <div className="flex-1">
        <p className="text-sm font-medium">{appName} Changelog Feed</p>
        <p className="text-xs text-gray-400">{entryCount} entries</p>
      </div>
      <div className="flex gap-2">
        <a href={feedUrl} className="rounded bg-orange-100 px-2.5 py-1 text-xs font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">RSS</a>
        {atomUrl && <a href={atomUrl} className="rounded bg-blue-100 px-2.5 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">Atom</a>}
      </div>
    </div>
  );
}
