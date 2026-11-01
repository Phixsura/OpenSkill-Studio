"use client";

import { useState } from "react";

interface EndpointStat {
  method: string;
  endpoint: string;
  hits: number;
  avgLatency: number;
  errorRate: number;
}

interface AnalyticsSummary {
  totalEndpoints: number;
  totalHits: number;
  totalErrors: number;
  overallErrorRate: number;
  avgLatency: number;
}

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-purple-600",
};

export function ApiAnalyticsPanel({
  summary,
  topEndpoints,
  slowest,
  errorProne,
}: {
  summary: AnalyticsSummary;
  topEndpoints: EndpointStat[];
  slowest: EndpointStat[];
  errorProne: EndpointStat[];
}) {
  const [tab, setTab] = useState<"top" | "slow" | "errors">("top");
  const displayed = tab === "top" ? topEndpoints : tab === "slow" ? slowest : errorProne;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📊 API Analytics</h2>
      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Endpoints</span>
          <span className="font-bold text-lg">{summary.totalEndpoints}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Hits</span>
          <span className="font-bold text-lg">{summary.totalHits.toLocaleString()}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Error Rate</span>
          <span className={`font-bold text-lg ${summary.overallErrorRate > 5 ? "text-red-600" : "text-green-600"}`}>{summary.overallErrorRate}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Avg Latency</span>
          <span className="font-bold text-lg">{summary.avgLatency}ms</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["top", "slow", "errors"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "top" ? "Most Hit" : t === "slow" ? "Slowest" : "Most Errors"}
          </button>
        ))}
      </div>

      <div className="space-y-0.5">
        {displayed.map((ep, i) => (
          <div key={`${ep.method}-${ep.endpoint}`} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">#{i + 1}</span>
              <span className={`text-xs font-bold ${methodColors[ep.method] || ""}`}>{ep.method}</span>
              <code className="text-xs">{ep.endpoint}</code>
            </div>
            <div className="flex gap-3 text-xs text-gray-500">
              <span>{ep.hits} hits</span>
              <span>{ep.avgLatency}ms</span>
              {ep.errorRate > 0 && <span className="text-red-500">{ep.errorRate}% err</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
