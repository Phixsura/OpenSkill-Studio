"use client";

interface ContentTypeInfo {
  destination: string;
  content_type: string;
  delivery_count: number;
}

interface APIWebhookContentTypeCardProps {
  configs: ContentTypeInfo[];
  defaultType: string;
  appName: string;
}

export default function APIWebhookContentTypeCard({ configs, defaultType, appName }: APIWebhookContentTypeCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📄 Content Types</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">default: {defaultType}</span>
      </div>

      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">All using default</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={c.destination} className="flex items-center justify-between text-[11px]">
              <span className="truncate max-w-[160px] text-gray-700 dark:text-gray-300">{c.destination}</span>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{c.content_type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
