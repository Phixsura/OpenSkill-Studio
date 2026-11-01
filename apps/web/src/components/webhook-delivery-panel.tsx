"use client";

import { useState } from "react";

interface WebhookDelivery {
  id: string;
  url: string;
  state: "queued" | "delivering" | "delivered" | "retrying" | "failed" | "dead_letter";
  attempts: number;
  maxRetries: number;
  lastStatusCode: number;
  lastError?: string;
  createdAt: string;
}

interface EndpointHealth {
  endpointId: string;
  url: string;
  circuitState: "closed" | "open" | "half_open";
  consecutiveFailures: number;
  totalDeliveries: number;
  totalFailures: number;
}

const stateStyles: Record<string, { color: string; icon: string }> = {
  queued: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏳" },
  delivering: { color: "bg-blue-100 text-blue-600 dark:bg-blue-900/30", icon: "🚀" },
  delivered: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  retrying: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "🔄" },
  failed: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "❌" },
  dead_letter: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", icon: "💀" },
};

const circuitStyles: Record<string, string> = {
  closed: "text-green-600", open: "text-red-600", half_open: "text-yellow-600",
};

export function WebhookDeliveryPanel({
  deliveries,
  endpoints,
  onResetCircuit,
  onRetryDeadLetter,
}: {
  deliveries: WebhookDelivery[];
  endpoints: EndpointHealth[];
  onResetCircuit?: (id: string) => void;
  onRetryDeadLetter?: (id: string) => void;
}) {
  const [tab, setTab] = useState<"deliveries" | "endpoints">("deliveries");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📬 Webhook Delivery</h2>

      <div className="flex gap-1">
        <button onClick={() => setTab("deliveries")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "deliveries" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Deliveries ({deliveries.length})
        </button>
        <button onClick={() => setTab("endpoints")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "endpoints" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Endpoints ({endpoints.length})
        </button>
      </div>

      {tab === "deliveries" && (
        <div className="space-y-2">
          {deliveries.map((d) => {
            const style = stateStyles[d.state] || stateStyles.failed;
            return (
              <div key={d.id} className="rounded-lg border dark:border-gray-700 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{style.icon}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded-full ${style.color}`}>{d.state}</span>
                    <span className="text-xs text-gray-400">{d.attempts}/{d.maxRetries}</span>
                  </div>
                  {d.state === "dead_letter" && (
                    <button onClick={() => onRetryDeadLetter?.(d.id)}
                      className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Retry</button>
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-1 truncate">{d.url}</div>
                {d.lastError && <div className="text-xs text-red-500 mt-0.5">{d.lastError}</div>}
              </div>
            );
          })}
        </div>
      )}

      {tab === "endpoints" && (
        <div className="space-y-2">
          {endpoints.map((ep) => (
            <div key={ep.endpointId} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-mono truncate max-w-xs">{ep.url}</div>
                  <div className="flex gap-3 text-xs text-gray-500 mt-1">
                    <span className={circuitStyles[ep.circuitState]}>● {ep.circuitState}</span>
                    <span>✓ {ep.totalDeliveries}</span>
                    <span className="text-red-500">✗ {ep.totalFailures}</span>
                  </div>
                </div>
                {ep.circuitState === "open" && (
                  <button onClick={() => onResetCircuit?.(ep.endpointId)}
                    className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Reset</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
