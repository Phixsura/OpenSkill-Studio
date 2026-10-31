"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

interface WebhookDelivery {
  id: string;
  event_type: string;
  event_id: string;
  url: string;
  status: string;
  http_status: number | null;
  attempt: number;
  max_attempts: number;
  error_message: string | null;
  duration_ms: number | null;
  created_at: string | null;
  delivered_at: string | null;
}

interface DeliveryStats {
  delivery_breakdown: Record<string, number>;
  avg_duration_ms: number;
  total: number;
}

const STATUS_COLORS: Record<string, string> = {
  DELIVERED: "text-green-600",
  PENDING: "text-yellow-600",
  RETRYING: "text-orange-600",
  FAILED: "text-red-600",
};

export default function WebhookDeliveriesPage() {
  const { appId } = useParams<{ appId: string }>();

  const { data: statsData } = useQuery({
    queryKey: ["webhook-stats", appId],
    queryFn: () =>
      apiWithAuth<{ data: DeliveryStats }>(
        `/developer/apps/${appId}/webhook-deliveries/stats`,
      ).then((r) => r.data),
  });

  const { data: deliveriesData, isLoading } = useQuery({
    queryKey: ["webhook-deliveries", appId],
    queryFn: () =>
      apiWithAuth<{ data: WebhookDelivery[]; meta: { total: number } }>(
        `/developer/apps/${appId}/webhook-deliveries?per_page=50`,
      ),
  });

  const stats = statsData;
  const deliveries = deliveriesData?.data ?? [];

  return (
    <div className="max-w-4xl p-8">
      <h1 className="mb-2 text-2xl font-bold">Webhook Deliveries</h1>
      <p className="mb-6 text-sm text-gray-500 dark:text-gray-400">
        Track webhook delivery status and performance
      </p>

      {/* Stats */}
      {stats && (
        <div className="mb-6 grid grid-cols-4 gap-4">
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Total</p>
            <p className="text-2xl font-bold">{stats.total}</p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Delivered</p>
            <p className="text-2xl font-bold text-green-600">
              {stats.delivery_breakdown.DELIVERED ?? 0}
            </p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Failed</p>
            <p className="text-2xl font-bold text-red-600">
              {stats.delivery_breakdown.FAILED ?? 0}
            </p>
          </div>
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <p className="text-sm text-gray-500">Avg Latency</p>
            <p className="text-2xl font-bold">{stats.avg_duration_ms.toFixed(0)}ms</p>
          </div>
        </div>
      )}

      {/* Delivery list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : deliveries.length === 0 ? (
        <div className="py-12 text-center text-gray-500 dark:text-gray-400">
          <p className="text-lg">No webhook deliveries yet</p>
          <p className="mt-1 text-sm">
            Deliveries will appear here when events are dispatched to your webhook URL
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {deliveries.map((d) => (
            <div key={d.id} className="rounded-lg border p-4 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-semibold ${STATUS_COLORS[d.status] ?? "text-gray-500"}`}>
                    {d.status}
                  </span>
                  <span className="font-mono text-sm">{d.event_type}</span>
                  {d.http_status && (
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs ${
                        d.http_status < 400
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {d.http_status}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-400">
                  {d.duration_ms !== null && <span>{d.duration_ms}ms</span>}
                  <span>
                    Attempt {d.attempt}/{d.max_attempts}
                  </span>
                  {d.created_at && (
                    <span>{new Date(d.created_at).toLocaleString()}</span>
                  )}
                </div>
              </div>
              {d.error_message && (
                <p className="mt-2 rounded bg-red-50 p-2 text-xs text-red-700 dark:bg-red-900/20 dark:text-red-400">
                  {d.error_message}
                </p>
              )}
              <p className="mt-1 truncate text-xs text-gray-400">→ {d.url}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
