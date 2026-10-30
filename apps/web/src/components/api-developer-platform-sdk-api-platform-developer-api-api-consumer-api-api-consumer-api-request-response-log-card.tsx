"use client";

interface Props { entryCount: number; avgDuration: number; totalBandwidthMb: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLogCard({ entryCount, avgDuration, totalBandwidthMb, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Request/Response Log</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{entryCount.toLocaleString()}</div><div className="text-gray-400">Entries</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{avgDuration}ms</div><div className="text-gray-400">Avg</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalBandwidthMb} MB</div><div className="text-gray-400">Bandwidth</div></div>
      </div>
    </div>
  );
}
