"use client";

interface DestMetricInfo {
  destination: string;
  deliveries: number;
  success_rate: number;
  avg_latency: number;
}

interface APIWebhookDeliveryMetricCardProps {
  destinations: DestMetricInfo[];
  appName: string;
}

export default function APIWebhookDeliveryMetricCard({ destinations, appName }: APIWebhookDeliveryMetricCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Delivery Metrics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{destinations.length} destinations</span>
      </div>

      {destinations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery metrics</p>
      ) : (
        <div className="space-y-1.5">
          {destinations.map((d) => (
            <div key={d.destination} className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="truncate max-w-[180px] text-xs text-gray-700 dark:text-gray-300">{d.destination}</span>
                <span className="text-[10px] text-gray-400">{d.deliveries} deliveries</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span className={d.success_rate < 95 ? "text-red-500" : ""}>{d.success_rate}% success</span>
                <span>{d.avg_latency}ms avg</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
