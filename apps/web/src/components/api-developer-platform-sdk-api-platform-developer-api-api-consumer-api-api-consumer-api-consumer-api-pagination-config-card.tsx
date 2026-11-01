"use client";

interface Props { consumerId: string; defaultSize: number; maxSize: number; strategy: string; cursorParam: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPaginationConfigCard({ consumerId, defaultSize, maxSize, strategy, cursorParam, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📄 Pagination Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="space-y-1 text-[11px]">
        <div className="flex justify-between"><span className="text-gray-500">Strategy:</span><span className="rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{strategy}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Default size:</span><span className="text-gray-700 dark:text-gray-300">{defaultSize}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Max size:</span><span className="text-gray-700 dark:text-gray-300">{maxSize}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Cursor param:</span><code className="text-gray-700 dark:text-gray-300">{cursorParam}</code></div>
      </div>
    </div>
  );
}
