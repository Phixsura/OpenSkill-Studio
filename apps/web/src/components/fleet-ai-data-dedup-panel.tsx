"use client";
export function FleetAiDataDedupPanel({ dedupers, active, processed, removed, reduction }: { dedupers: number; active: number; processed: number; removed: number; reduction: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧹 AI Data Dedup</h3>
    <div className="text-sm">{active}/{dedupers} active · {processed.toLocaleString()} processed · {removed.toLocaleString()} removed · {reduction}% reduction</div>
  </div>);
}
