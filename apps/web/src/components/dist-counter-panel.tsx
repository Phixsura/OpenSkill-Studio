"use client";
interface DistCounterPanelProps { total: number; shardValues: number[]; shards: number; }
export function DistCounterPanel({ total, shardValues, shards }: DistCounterPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔢 Distributed Counter</h3>
        <span className="text-xs text-gray-400">{shards} shards · total: {total.toLocaleString()}</span>
      </div>
      <div className="flex gap-1 p-4">
        {shardValues.map((v, i) => (
          <div key={i} className="flex-1 text-center text-xs">
            <div className="font-bold">{v.toLocaleString()}</div>
            <div className="text-gray-400">shard-{i}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
