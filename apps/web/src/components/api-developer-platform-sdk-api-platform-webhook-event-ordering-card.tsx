"use client";

interface PartitionInfo { partition_key: string; last_delivered_seq: number; pending_count: number; out_of_order_count: number; }
interface Props { partitions: PartitionInfo[]; outOfOrderCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformWebhookEventOrderingCard({ partitions, outOfOrderCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔢 Event Ordering</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {partitions.length} partitions</p>
        </div>
        {outOfOrderCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{outOfOrderCount} out of order</span>}
      </div>
      {partitions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No ordering data</p>
      ) : (
        <div className="space-y-1">
          {partitions.slice(0, 5).map((p) => (
            <div key={p.partition_key} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{p.partition_key}</span>
              <span className="text-gray-400">seq:{p.last_delivered_seq} · {p.pending_count} pending{p.out_of_order_count > 0 ? ` · ${p.out_of_order_count} ooo` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
