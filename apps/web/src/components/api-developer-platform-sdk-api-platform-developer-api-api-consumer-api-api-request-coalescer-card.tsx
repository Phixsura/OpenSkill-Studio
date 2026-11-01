"use client";

interface Props { coalesceRate: number; totalRequests: number; coalesced: number; pendingCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCoalescerCard({ coalesceRate, totalRequests, coalesced, pendingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Request Coalescer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-green-600 dark:text-green-400">{coalesceRate}% saved</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalRequests.toLocaleString()}</div><div className="text-gray-400">Total</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{coalesced.toLocaleString()}</div><div className="text-gray-400">Coalesced</div></div>
        <div><div className="font-semibold text-yellow-600 dark:text-yellow-400">{pendingCount}</div><div className="text-gray-400">Pending</div></div>
      </div>
    </div>
  );
}
