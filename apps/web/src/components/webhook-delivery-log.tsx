"use client";

import { useState } from "react";

interface DeliveryAttempt {
  attempt: number;
  status_code: number | null;
  latency_ms: number;
  error: string | null;
  timestamp: string;
  success: boolean;
}

interface WebhookDelivery {
  id: string;
  event_type: string;
  url: string;
  status: "delivered" | "retrying" | "dead_letter" | "pending" | "cancelled";
  attempt_count: number;
  max_attempts: number;
  next_retry_at: string | null;
  created_at: string;
  attempts: DeliveryAttempt[];
}

interface WebhookDeliveryLogProps {
  deliveries: WebhookDelivery[];
  onReplay: (id: string) => void;
  onCancel: (id: string) => void;
  totalCount: number;
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  delivered: {
    label: "Delivered",
    color: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    icon: "✓",
  },
  retrying: {
    label: "Retrying",
    color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    icon: "↻",
  },
  dead_letter: {
    label: "Failed",
    color: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    icon: "✗",
  },
  pending: {
    label: "Pending",
    color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    icon: "…",
  },
  cancelled: {
    label: "Cancelled",
    color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
    icon: "⊘",
  },
};

function StatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.pending;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.color}`}
    >
      <span>{config.icon}</span>
      {config.label}
    </span>
  );
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return iso;
  }
}

function DeliveryRow({
  delivery,
  onReplay,
  onCancel,
}: {
  delivery: WebhookDelivery;
  onReplay: (id: string) => void;
  onCancel: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border-b border-gray-100 last:border-0 dark:border-gray-800">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50"
        aria-expanded={expanded}
        aria-label={`Toggle details for ${delivery.event_type}`}
      >
        <StatusBadge status={delivery.status} />
        <span className="flex-1 truncate font-mono text-sm">{delivery.event_type}</span>
        <span className="hidden text-xs text-gray-400 sm:block">{delivery.url}</span>
        <span className="text-xs text-gray-400">{formatTime(delivery.created_at)}</span>
        <span className="text-gray-400">{expanded ? "▾" : "▸"}</span>
      </button>

      {expanded && (
        <div className="bg-gray-50 px-4 pb-3 dark:bg-gray-800/30">
          <div className="mb-2 flex items-center gap-2 text-xs text-gray-500">
            <span>
              Attempts: {delivery.attempt_count}/{delivery.max_attempts}
            </span>
            {delivery.next_retry_at && (
              <span>• Next retry: {formatTime(delivery.next_retry_at)}</span>
            )}
          </div>

          {delivery.attempts.length > 0 && (
            <table className="w-full text-xs" role="table" aria-label="Delivery attempts">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="pb-1 pr-3">#</th>
                  <th className="pb-1 pr-3">Status</th>
                  <th className="pb-1 pr-3">Latency</th>
                  <th className="pb-1">Error</th>
                </tr>
              </thead>
              <tbody>
                {delivery.attempts.map((a) => (
                  <tr key={a.attempt} className="border-t border-gray-200 dark:border-gray-700">
                    <td className="py-1 pr-3">{a.attempt}</td>
                    <td className="py-1 pr-3">
                      {a.success ? (
                        <span className="text-green-600">{a.status_code}</span>
                      ) : (
                        <span className="text-red-600">{a.status_code ?? "—"}</span>
                      )}
                    </td>
                    <td className="py-1 pr-3">{a.latency_ms.toFixed(0)}ms</td>
                    <td className="truncate py-1 text-gray-400">{a.error ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="mt-2 flex gap-2">
            {delivery.status === "dead_letter" && (
              <button
                onClick={() => onReplay(delivery.id)}
                className="rounded border border-blue-300 px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-400 dark:hover:bg-blue-900/20"
              >
                Replay
              </button>
            )}
            {(delivery.status === "pending" || delivery.status === "retrying") && (
              <button
                onClick={() => onCancel(delivery.id)}
                className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export function WebhookDeliveryLog({
  deliveries,
  onReplay,
  onCancel,
  totalCount,
}: WebhookDeliveryLogProps) {
  const delivered = deliveries.filter((d) => d.status === "delivered").length;
  const failing = deliveries.filter(
    (d) => d.status === "dead_letter" || d.status === "retrying",
  ).length;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">Webhook Deliveries</h3>
          <p className="text-xs text-gray-500">
            {totalCount} total • {delivered} delivered • {failing} failing
          </p>
        </div>
      </div>

      {deliveries.length === 0 ? (
        <div className="py-8 text-center">
          <span className="text-3xl">📡</span>
          <p className="mt-2 text-sm text-gray-500">No webhook deliveries yet</p>
        </div>
      ) : (
        <div role="list" aria-label="Webhook deliveries">
          {deliveries.map((d) => (
            <DeliveryRow key={d.id} delivery={d} onReplay={onReplay} onCancel={onCancel} />
          ))}
        </div>
      )}
    </div>
  );
}
