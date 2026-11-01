"use client";

interface ConfigInfo { consumer_id: string; default_page_size: number; max_page_size: number; style: string; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponsePaginationCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📄 Pagination</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} configs</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pagination configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <span className="text-gray-400">{c.style} · {c.default_page_size}/{c.max_page_size}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
