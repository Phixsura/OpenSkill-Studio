"use client";

interface WebhookDelivery {
  id: string;
  event_type: string;
  url: string;
  status: "pending" | "delivered" | "failed" | "retrying";
  http_status: number | null;
  attempt: number;
  duration_ms: number | null;
  created_at: string;
}

interface WebhookStatusProps {
  deliveries: WebhookDelivery[];
}

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  pending: { bg: "bg-yellow-100 dark:bg-yellow-900", text: "text-yellow-800 dark:text-yellow-200", label: "Pending" },
  delivered: { bg: "bg-green-100 dark:bg-green-900", text: "text-green-800 dark:text-green-200", label: "Delivered" },
  failed: { bg: "bg-red-100 dark:bg-red-900", text: "text-red-800 dark:text-red-200", label: "Failed" },
  retrying: { bg: "bg-blue-100 dark:bg-blue-900", text: "text-blue-800 dark:text-blue-200", label: "Retrying" },
};

export function WebhookStatus({ deliveries }: WebhookStatusProps) {
  if (deliveries.length === 0) {
    return <p className="py-4 text-center text-sm text-gray-400">No webhook deliveries</p>;
  }

  return (
    <div className="space-y-2">
      {deliveries.map((d) => {
        const style = STATUS_STYLES[d.status] ?? STATUS_STYLES.pending;
        return (
          <div key={d.id} className="flex items-center justify-between rounded border border-gray-200 p-3 dark:border-gray-700">
            <div className="flex-1">
              <span className="text-sm font-medium">{d.event_type}</span>
              <span className="ml-2 text-xs text-gray-500">{d.url}</span>
            </div>
            <div className="flex items-center gap-3">
              {d.http_status && <span className="text-xs text-gray-500">HTTP {d.http_status}</span>}
              {d.duration_ms != null && <span className="text-xs text-gray-400">{d.duration_ms}ms</span>}
              <span className="text-xs text-gray-400">#{d.attempt}</span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${style.bg} ${style.text}`}>
                {style.label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
