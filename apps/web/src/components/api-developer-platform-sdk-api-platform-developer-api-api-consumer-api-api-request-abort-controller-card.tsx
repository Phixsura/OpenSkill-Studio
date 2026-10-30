"use client";

interface Props { inFlightCount: number; abortRate: number; totalAborted: number; totalCompleted: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAbortControllerCard({ inFlightCount, abortRate, totalAborted, totalCompleted, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛑 Abort Controller</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{abortRate}% abort rate</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-blue-600 dark:text-blue-400">{inFlightCount}</div><div className="text-gray-400">In Flight</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{totalCompleted}</div><div className="text-gray-400">Completed</div></div>
        <div><div className="font-semibold text-red-600 dark:text-red-400">{totalAborted}</div><div className="text-gray-400">Aborted</div></div>
      </div>
    </div>
  );
}
