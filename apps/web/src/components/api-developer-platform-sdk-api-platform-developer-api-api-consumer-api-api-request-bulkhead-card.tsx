"use client";

interface PartitionInfo { partition_id: string; name: string; max_concurrent: number; active: number; rejected: number; utilization: number; }
interface Props { partitions: PartitionInfo[]; appName: string; }

const barColor = (u: number) => u >= 90 ? "bg-red-500" : u >= 70 ? "bg-yellow-500" : "bg-green-500";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBulkheadCard({ partitions, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧱 Request Bulkhead</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {partitions.length} partitions</p>
      </div>
      {partitions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No bulkhead partitions</p>
      ) : (
        <div className="space-y-2">
          {partitions.map((p) => (
            <div key={p.partition_id} className="text-[11px]">
              <div className="flex justify-between"><span className="text-gray-700 dark:text-gray-300">{p.name}</span><span className="text-gray-400">{p.active}/{p.max_concurrent} · {p.rejected} rejected</span></div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800"><div className={`h-1 rounded-full ${barColor(p.utilization)}`} style={{ width: `${p.utilization}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
