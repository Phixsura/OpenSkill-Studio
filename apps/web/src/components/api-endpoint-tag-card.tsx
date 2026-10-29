"use client";

interface TagCount {
  tag: string;
  count: number;
}

interface APIEndpointTagCardProps {
  tags: TagCount[];
  totalEndpoints: number;
  appName: string;
}

export default function APIEndpointTagCard({ tags, totalEndpoints, appName }: APIEndpointTagCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Endpoint Tags</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{tags.length} tags · {totalEndpoints} endpoints</span>
      </div>

      {tags.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoint tags</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {tags.map((t) => (
            <span key={t.tag} className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-1 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300">
              {t.tag}
              <span className="rounded-full bg-gray-200 px-1.5 py-0.5 text-[9px] text-gray-500 dark:bg-gray-700">{t.count}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
