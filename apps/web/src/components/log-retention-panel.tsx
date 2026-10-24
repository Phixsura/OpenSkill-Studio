"use client";
interface LogRetentionPanelProps { toKeep: number; toDelete: number; sizeFreedMb: number;
  currentGb: number; maxProjectedGb: number; retentionDays: number; }
export function LogRetentionPanel({ toKeep, toDelete, sizeFreedMb, currentGb, maxProjectedGb, retentionDays }: LogRetentionPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Log Retention</h3>
        <span className="text-xs text-gray-400">{retentionDays}d policy · {sizeFreedMb}MB reclaimable</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Keep</span><div className="font-bold text-green-600 text-lg">{toKeep}</div></div>
        <div><span className="text-gray-400">Delete</span><div className="font-bold text-red-500 text-lg">{toDelete}</div></div>
        <div><span className="text-gray-400">Storage</span><div className="font-bold text-lg">{currentGb}/{maxProjectedGb}GB</div></div>
      </div>
    </div>
  );
}
