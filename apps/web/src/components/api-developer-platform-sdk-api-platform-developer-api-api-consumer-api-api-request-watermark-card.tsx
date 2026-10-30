"use client";

interface Props { generated: number; verified: number; totalWatermarks: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermarkCard({ generated, verified, totalWatermarks, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💧 Request Watermarks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalWatermarks.toLocaleString()}</div><div className="text-gray-400">Total</div></div>
        <div><div className="font-semibold text-blue-600 dark:text-blue-400">{generated.toLocaleString()}</div><div className="text-gray-400">Generated</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{verified.toLocaleString()}</div><div className="text-gray-400">Verified</div></div>
      </div>
    </div>
  );
}
