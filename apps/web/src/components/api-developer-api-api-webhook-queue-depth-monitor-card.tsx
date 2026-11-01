"use client";

interface SnapshotInfo { destination: string; depth: number; oldest_age_seconds: number; estimated_drain_seconds: number; backlogged: boolean; }
interface Props { snapshots: SnapshotInfo[]; totalDepth: number; backloggedCount: number; appName: string; }

export default function APIDeveloperAPIApiWebhookQueueDepthMonitorCard({ snapshots, totalDepth, backloggedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Queue Depth</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-sm font-bold text-blue-600">{totalDepth.toLocaleString()}</span>
          {backloggedCount > 0 && <p className="text-[9px] text-red-500">{backloggedCount} backlogged</p>}
        </div>
      </div>
      {snapshots.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No queue data</p>
      ) : (
        <div className="space-y-1.5">
          {snapshots.map((s) => (
            <div key={s.destination} className="flex items-center justify-between text-[11px]">
              <span className={`text-gray-700 dark:text-gray-300 ${s.backlogged ? "font-bold text-red-500" : ""}`}>{new URL(s.destination).hostname}</span>
              <span className="text-gray-400">{s.depth} msgs · drain: {s.estimated_drain_seconds}s</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
