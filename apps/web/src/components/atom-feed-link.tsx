"use client";

interface AtomFeedLinkProps { appName: string; feedUrl: string; entryCount: number;
  onCopy: () => void; onSubscribe: () => void; }

export function AtomFeedLink({ appName, feedUrl, entryCount, onCopy, onSubscribe }: AtomFeedLinkProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <span className="text-xl">📡</span>
        <div>
          <p className="text-sm font-medium">{appName} Atom Feed</p>
          <p className="text-xs text-gray-400">{entryCount} entries</p>
        </div>
      </div>
      <div className="flex gap-2">
        <button onClick={onCopy} className="rounded border px-2.5 py-1 text-xs dark:border-gray-600">Copy URL</button>
        <button onClick={onSubscribe} className="rounded bg-orange-500 px-2.5 py-1 text-xs text-white">Subscribe</button>
      </div>
    </div>
  );
}
