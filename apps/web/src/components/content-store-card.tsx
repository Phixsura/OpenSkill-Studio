"use client";

interface ContentItem {
  key: string;
  content_type: string;
  size_bytes: number;
  version: number;
  updated_at: string;
}

interface ContentStoreCardProps {
  items: ContentItem[];
  appName: string;
  totalSizeBytes: number;
  maxSizeBytes: number;
}

function formatBytes(b: number): string {
  if (b >= 1024 * 1024) return `${(b / (1024 * 1024)).toFixed(1)} MB`;
  if (b >= 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${b} B`;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function ContentStoreCard({
  items,
  appName,
  totalSizeBytes,
  maxSizeBytes,
}: ContentStoreCardProps) {
  const usagePct = maxSizeBytes > 0 ? Math.min((totalSizeBytes / maxSizeBytes) * 100, 100) : 0;
  const barColor = usagePct >= 90 ? "bg-red-500" : usagePct >= 70 ? "bg-yellow-500" : "bg-blue-500";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Content Store</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{items.length} items</span>
      </div>

      {/* Storage bar */}
      <div className="mb-4">
        <div className="mb-1 flex items-center justify-between text-[11px] text-gray-500">
          <span>Storage</span>
          <span>
            {formatBytes(totalSizeBytes)} / {formatBytes(maxSizeBytes)}
          </span>
        </div>
        <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${usagePct}%` }} />
        </div>
      </div>

      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No content stored</p>
      ) : (
        <div className="space-y-1.5">
          {items.map((item) => (
            <div
              key={item.key}
              className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                  {item.key}
                </span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                  {item.content_type}
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-gray-400">
                <span>v{item.version}</span>
                <span>{formatBytes(item.size_bytes)}</span>
                <span>{timeAgo(item.updated_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
