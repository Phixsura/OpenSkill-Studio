"use client";

interface Props { decompressedCount: number; totalInKb: number; totalOutKb: number; maxSizeKb: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressorCard({ decompressedCount, totalInKb, totalOutKb, maxSizeKb, appName }: Props) {
  const savings = totalOutKb > 0 ? Math.round((1 - totalInKb / totalOutKb) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗜️ Request Decompressor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — max {maxSizeKb} KB</p>
        </div>
        <span className="text-[10px] text-gray-400">{savings}% compression</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{decompressedCount.toLocaleString()}</div><div className="text-gray-400">Processed</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalInKb} KB</div><div className="text-gray-400">In</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalOutKb} KB</div><div className="text-gray-400">Out</div></div>
      </div>
    </div>
  );
}
