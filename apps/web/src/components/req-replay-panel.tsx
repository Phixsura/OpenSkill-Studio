"use client";
interface ReqReplayPanelProps { captured: number; replayed: number; maxBuffer: number; }
export function ReqReplayPanel({ captured, replayed, maxBuffer }: ReqReplayPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏮️ Request Replay</h3>
        <span className="text-xs text-gray-400">{captured}/{maxBuffer} captured · {replayed} replayed</span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Buffer</span>
          <span>{captured}/{maxBuffer}</span>
        </div>
        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${captured / maxBuffer * 100}%` }} />
        </div>
      </div>
    </div>
  );
}
