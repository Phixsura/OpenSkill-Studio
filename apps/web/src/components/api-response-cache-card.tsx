"use client";

interface APIResponseCacheCardProps {
  cacheSize: number;
  hitRate: number;
  totalHits: number;
  totalMisses: number;
  appName: string;
}

export default function APIResponseCacheCard({ cacheSize, hitRate, totalHits, totalMisses, appName }: APIResponseCacheCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💾 Response Cache</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{cacheSize} entries</span>
      </div>

      <div className="mb-3 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className={`text-lg font-bold ${hitRate >= 80 ? "text-green-600" : hitRate >= 50 ? "text-yellow-600" : "text-red-500"}`}>{hitRate}%</p>
          <p className="text-[9px] text-gray-500">hit rate</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-green-600">{totalHits}</p>
          <p className="text-[9px] text-gray-500">hits</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{totalMisses}</p>
          <p className="text-[9px] text-gray-500">misses</p>
        </div>
      </div>
    </div>
  );
}
