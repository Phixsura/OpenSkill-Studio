"use client";

import { useState } from "react";

interface LatencyStats {
  count: number;
  avg: number;
  p50: number;
  p95: number;
  p99: number;
  max: number;
}

interface BandwidthInfo {
  totalMb: number;
  limitMb: number;
  usagePercent: number;
}

interface TopEndpoint {
  url: string;
  count: number;
}

interface Anomaly {
  message: string;
}

export function NetworkMonitorPanel({
  totalRequests,
  errorRate,
  bandwidth,
  latency,
  topEndpoints,
  anomalies,
}: {
  totalRequests: number;
  errorRate: number;
  bandwidth: BandwidthInfo;
  latency: LatencyStats;
  topEndpoints: TopEndpoint[];
  anomalies: Anomaly[];
}) {
  const [tab, setTab] = useState<"overview" | "endpoints" | "anomalies">("overview");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🌐 Network Monitor</h2>

      <div className="grid grid-cols-4 gap-2 text-center">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Requests</span>
          <span className="font-bold">{totalRequests.toLocaleString()}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Error Rate</span>
          <span className={`font-bold ${errorRate > 10 ? "text-red-600" : "text-green-600"}`}>{errorRate}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Bandwidth</span>
          <span className="font-bold">{bandwidth.totalMb}MB</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Avg Latency</span>
          <span className="font-bold">{latency.avg}ms</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["overview", "endpoints", "anomalies"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "overview" ? "Latency" : t === "endpoints" ? `Top Endpoints (${topEndpoints.length})` : `Anomalies (${anomalies.length})`}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="grid grid-cols-5 gap-2 text-center text-xs">
          {[
            { label: "p50", value: latency.p50 },
            { label: "p95", value: latency.p95 },
            { label: "p99", value: latency.p99 },
            { label: "max", value: latency.max },
            { label: "count", value: latency.count },
          ].map((item) => (
            <div key={item.label} className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-400 block">{item.label}</span>
              <span className="font-bold">{item.value}{item.label !== "count" ? "ms" : ""}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "endpoints" && (
        <div className="space-y-1">
          {topEndpoints.map((ep, i) => (
            <div key={ep.url} className="flex items-center justify-between rounded-lg border dark:border-gray-700 p-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 font-mono w-5">#{i + 1}</span>
                <code className="text-xs truncate max-w-xs">{ep.url}</code>
              </div>
              <span className="font-bold text-xs">{ep.count}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "anomalies" && (
        <div className="space-y-1">
          {anomalies.length === 0 && <span className="text-sm text-gray-500">No anomalies detected</span>}
          {anomalies.map((a, i) => (
            <div key={i} className="text-xs text-red-500 rounded-lg border border-red-300 dark:border-red-700 p-2">
              ⚠ {a.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
