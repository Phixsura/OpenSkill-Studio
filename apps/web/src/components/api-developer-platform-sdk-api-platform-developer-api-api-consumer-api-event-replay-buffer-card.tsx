"use client";

interface Props { totalBuffered: number; pendingReplay: number; bufferSizeKb: number; maxBufferSize: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiEventReplayBufferCard({ totalBuffered, pendingReplay, bufferSizeKb, maxBufferSize, appName }: Props) {
  const usagePct = maxBufferSize > 0 ? Math.round((totalBuffered / maxBufferSize) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💾 Replay Buffer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {pendingReplay > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">{pendingReplay} pending</span>}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalBuffered.toLocaleString()}</div><div className="text-gray-400">Buffered</div></div>
        <div><div className="font-semibold text-yellow-600">{pendingReplay}</div><div className="text-gray-400">Pending</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{bufferSizeKb} KB</div><div className="text-gray-400">Size</div></div>
      </div>
      <div className="mt-2 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1 rounded-full bg-blue-500" style={{ width: `${usagePct}%` }} />
      </div>
    </div>
  );
}
