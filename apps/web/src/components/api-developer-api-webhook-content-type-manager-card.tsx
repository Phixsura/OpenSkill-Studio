"use client";

interface ConfigInfo { destination: string; content_type: string; charset: string; delivery_count: number; }
interface Props { configs: ConfigInfo[]; contentTypeBreakdown: Record<string, number>; appName: string; }

export default function APIDeveloperAPIWebhookContentTypeManagerCard({ configs, contentTypeBreakdown, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Content Types</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} destinations</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1.5">
        {Object.entries(contentTypeBreakdown).map(([ct, count]) => (
          <span key={ct} className="rounded bg-purple-50 px-1.5 py-0.5 text-[10px] text-purple-700 dark:bg-purple-900 dark:text-purple-200">{ct.split("/")[1]}: {count}</span>
        ))}
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No content type configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.destination} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.destination}</span>
              <span className="text-gray-400">{c.content_type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
