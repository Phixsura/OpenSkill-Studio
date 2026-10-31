"use client";

interface Props { totalCorrelations: number; avgChainDepth: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestCorrelationIdCard({ totalCorrelations, avgChainDepth, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Correlation IDs</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalCorrelations.toLocaleString()}</div><div className="text-gray-400">Total</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{avgChainDepth}</div><div className="text-gray-400">Avg Depth</div></div>
      </div>
    </div>
  );
}
