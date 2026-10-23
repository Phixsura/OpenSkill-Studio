"use client";

interface BucketInfo { name: string; size_gb: number; objects: number; }
interface StorageUsagePanelProps { buckets: BucketInfo[]; totalSizeGb: number; totalObjects: number;
  onCreate: () => void; }

export function StorageUsagePanel({ buckets, totalSizeGb, totalObjects, onCreate }: StorageUsagePanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Storage</h2>
        <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">New Bucket</button>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{totalSizeGb} GB</p>
          <p className="text-xs text-gray-400">Total Size</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{totalObjects.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Objects</p>
        </div>
      </div>
      <div className="space-y-1.5">
        {buckets.map(b => {
          const pct = totalSizeGb > 0 ? Math.round((b.size_gb / totalSizeGb) * 100) : 0;
          return (
            <div key={b.name} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
              <span className="text-lg">📦</span>
              <span className="flex-1 font-medium">{b.name}</span>
              <span className="text-xs text-gray-400">{b.size_gb} GB · {b.objects} files</span>
              <div className="h-2 w-16 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
