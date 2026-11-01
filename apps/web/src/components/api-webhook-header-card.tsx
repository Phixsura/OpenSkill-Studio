"use client";

interface HeaderInfo {
  name: string;
  value: string;
  secret: boolean;
}

interface APIWebhookHeaderCardProps {
  destination: string;
  headers: HeaderInfo[];
  appName: string;
}

export default function APIWebhookHeaderCard({ destination, headers, appName }: APIWebhookHeaderCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📨 Webhook Headers</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{headers.length} headers</span>
      </div>

      <p className="mb-2 truncate text-[10px] text-gray-400">{destination}</p>

      {headers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom headers</p>
      ) : (
        <div className="space-y-1">
          {headers.map((h) => (
            <div key={h.name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-700 dark:text-gray-300">{h.name}</span>
                {h.secret && <span className="text-[9px] text-orange-500">🔒</span>}
              </div>
              <span className="font-mono text-gray-400">{h.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
