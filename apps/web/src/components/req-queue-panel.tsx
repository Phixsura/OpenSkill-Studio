"use client";

interface ReqQueuePanelProps { queueSize: number; dlqSize: number; processed: number; maxRetries: number; }

export function ReqQueuePanel({ queueSize, dlqSize, processed, maxRetries }: ReqQueuePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📬 Request Queue</h3>
        <span className="text-xs text-gray-400">max {maxRetries} retries</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Queued</div><div className="font-bold text-lg text-blue-500">{queueSize}</div></div>
        <div><div className="text-gray-400">Processed</div><div className="font-bold text-lg text-green-600">{processed.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Dead Letter</div><div className={`font-bold text-lg ${dlqSize > 0 ? "text-red-500" : "text-gray-400"}`}>{dlqSize}</div></div>
      </div>
    </div>
  );
}
