"use client";

interface EndpointInfo {
  endpoint_id: string;
  url: string;
  events: string[];
  enabled: boolean;
  success_rate: number;
  total_deliveries: number;
}

interface WebhookEndpointCardProps {
  endpoints: EndpointInfo[];
  appName: string;
}

export default function WebhookEndpointCard({ endpoints, appName }: WebhookEndpointCardProps) {
  const enabled = endpoints.filter((e) => e.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🎯 Webhook Endpoints
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {enabled}/{endpoints.length} enabled
        </span>
      </div>

      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No webhook endpoints</p>
      ) : (
        <div className="space-y-2">
          {endpoints.map((ep) => (
            <div
              key={ep.endpoint_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!ep.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <span className="max-w-[200px] truncate text-xs text-gray-700 dark:text-gray-300">
                  {ep.url}
                </span>
                <span className="text-[10px] text-gray-400">{ep.success_rate}%</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {ep.events.slice(0, 3).map((e) => (
                  <span
                    key={e}
                    className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                  >
                    {e}
                  </span>
                ))}
                {ep.events.length > 3 && (
                  <span className="text-[9px] text-gray-400">+{ep.events.length - 3}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
