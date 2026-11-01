"use client";

interface Bucket { name: string; region: string; objects: number; sizeMb: number; public: boolean; }
interface StorageBucketBrowserProps { buckets: Bucket[]; totalObjects: number;
  totalSizeMb: number; onCreate: () => void; }

export function StorageBucketBrowser({ buckets, totalObjects, totalSizeMb, onCreate }: StorageBucketBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪣 Storage Buckets</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{totalObjects} objects · {totalSizeMb} MB</span>
          <button onClick={onCreate} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ New</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {buckets.map(b => (
          <div key={b.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm font-mono font-medium">{b.name}</div>
              <div className="text-[10px] text-gray-400">{b.region} · {b.objects} objects · {b.sizeMb} MB</div>
            </div>
            <span className={`text-[10px] px-1.5 py-0.5 rounded ${b.public ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600"}`}>
              {b.public ? "Public" : "Private"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
